import concurrent.futures
import numpy as np
import time
import pickle
import sys
from tqdm import *
import random
import os
path = 'file_uploaded/file_'
file_log = ""


days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
mouths = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
id_process = 1 #id of start process


def set_proc_data(np, file, number_process, type_file):
    file.seek(0, 2)
    filesz = file.tell()
    byte_for_proc = int(filesz / np)
    ll = []
    for _ in range(np):
        ll.append("")
    #print("file size: " + str(filesz))
    #print("byte_min_proc: " + str(byte_for_proc))
    #print("expected number of process: "+str(number_process))
    list_read_byte = data_for_proc_rec(byte_for_proc, np, file, 0, ll, filesz, type_file)
    return list_read_byte


def data_for_proc_rec(byte, num_p, file, id_proc, list, filesz , type_file):
    if id_proc == 0:
        file.seek(byte, 0)
        if id_proc == num_p-1:    #exception for just one process
            list[id_proc] = filesz
            return list
    elif id_proc == num_p-1:
        list[id_proc] = filesz
        return list
    else:
        file.seek(int(list[id_proc-1])+int(byte), 0)
    ex = False
    line = "asd"
    while not ex and line:
        line = file.readline()
        #print("line: "+line)
        for word in line.split():
            if type_file == "log":
                if word in days:
                    #print("w at: " + str(file.tell() - len(line)))
                    list[id_proc] = file.tell() - len(line)
                    ex = True
            elif type_file == "txt":
                if word in mouths:
                    # print("w at: " + str(file.tell() - len(line)))
                    list[id_proc] = file.tell() - len(line)
                    ex = True
    return data_for_proc_rec(byte, num_p, file, id_proc + 1, list, filesz, type_file)

def create_np_array(number_sens):
    x = np.array([["Data"]])
    for id in range(number_sens):
        x = np.append(x, [["Risc_"+str(id+1)], ["Signal_"+str(id+1)], ["Volt_"+str(id+1)]])
    x = np.append(x, [["Temp"], ["Rh%"]])
    return x


def type_line(line):
    word = line[0:3]
    if len(line) == 1:
        return -1
    elif word in days:
        return 0
    elif word[0] == 'S' and  word[1].isnumeric() and word[2].isnumeric():
        return 1
    elif word[0] == 'T' and word[1] == ':':
        return 2
    else:
        return -1


def is_broken_line(line):
    if len(line) == 1:
        return -1
    for word in line.split():
        if word in days:
            return 0
        elif word[0] == 'S' and  word[1].isnumeric() and word[2].isnumeric():
            return 1
        elif word[0] == 'T' and word[1] == ':':
            return 2
    return -2                                       #non itera se la riga è vuota, ma il primo if non funziona boh


def take_datatime(line):
    str = ""
    save = False
    for word in line.split():
        if word in mouths:
            save = True
        if "GMT" in word:
            save = False
        if save:
            str += " "+word
    return str


def recovery_list(file, start_byte, number_sensor):
    exit = False
    file.seek(start_byte, 0)
    supp_list = []
    for _ in range((number_sensor * 3) + 3):
        supp_list.append("NaN")
    while not exit:
        line = file.readline()
        tp = type_line(line)
        if tp == -1:
            tp = is_broken_line(line)
        if tp == 0:
            supp_list[0]= take_datatime(line)
        elif tp == 1:
            sens_data = line.split(":")
            for id in range(3):
                supp_list[(((int(sens_data[0][1]))-1)*3)+1+id] = (float(sens_data[id + 1]))
        elif tp == 2:
            sens_data = line.split(":")
            take = False
            last = -2
            for w in sens_data:
                if take:
                    supp_list[last] = (float(w))
                    last += 1
                    take = False
                if "T" == w or "H" == w:
                    take = True
            exit = True
        elif tp == -1:
            exit = True
    return supp_list


def get_data(start, end, file, number_sens, id_process):
    #print("process created with id: "+str(id_process)+", read_byte from "+str(start)+" to "+str(end))
    firsttime = True
    thereisdata = False
    there_is_corrupt_data = False
    file.seek(start, 0)
    seek = start
    list = []
    total_byte = end - start
    txt = "PROCESS " + str(id_process)+ " "
    wr = 0
    bb = 0
    with tqdm(total=total_byte, file=sys.stdout, position=0, leave=True, desc=txt) as pbar:
        while seek < end:
            wr = wr + 1
            if wr > 1000:
                pbar.update(bb)
                wr = 0
                bb = 0
            line = file.readline()
            bb = bb + len(line)
            tp = type_line(line)
            if tp == -1:
                tp = is_broken_line(line)
            if tp == 0:
                first_byte_mis = int(file.tell())-len(line)
                there_is_corrupt_data = False
                thereisdata = True
                list = []
                list.append(take_datatime(line))
            elif tp == 1:
                thereisdata = True
                sens_data = line.split(":")
                for id in range(3):
                    list.append(float(sens_data[id+1]))
            elif tp == 2:
                thereisdata = True
                gen_data = line.split(":")
                take = False
                for w in gen_data:
                    if take:
                        list.append(float(w))
                        take = False
                    if "T" == w or "H" == w:
                        take = True
            elif tp == -2:
                there_is_corrupt_data = True
            else:
                if not there_is_corrupt_data:
                    if thereisdata and len(list) != (number_sens*3)+3:
                        list = recovery_list(file, first_byte_mis, number_sens)
                        first_byte_mis = int(file.tell())
                    if thereisdata and firsttime:
                        thereisdata = False
                        array_data = np.array([list], dtype=str)
                        firsttime = False
                    elif thereisdata:
                        thereisdata = False
                        array_data = np.append(array_data, [list], axis=0)
            seek = file.tell()
    return array_data


def get_data_txt(file, seek, end, id_process):
    file.seek(seek, 0)
    seek_tmp = file.tell()
    if id_process == 1:
        line = file.readline()
    line = file.readline()
    ll = []
    first = True
    total_byte = end - seek
    txt = "PROCESS " + str(id_process) + " "
    wr = 0
    bb = 0
    with tqdm(total=total_byte, file=sys.stdout, position=0, leave=True, desc=txt) as pbar:
        while line and int(seek_tmp) <= end:
            wr = wr + 1
            if wr > 50:
                pbar.update(bb)
                wr = 0
                bb = 0
            bb = bb + len(line)
            line = line.split('\t')
            #ll.append(line[0]+" "+line[1]+" "+line[2]+" "+line[3])
            for id in range(0, len(line)):
                ll.append(line[id])
            if first:
                m = np.array([ll])
                first = False
            else:
                m = np.append(m, [ll], axis=0)
            ll = []
            line = file.readline()
            seek_tmp = file.tell()
    return m


def add_result(file, process, number_sensor, type_file):
    ll = set_proc_data(process, file, process, type_file)
    ll.insert(0, 0)
    if type_file == "log":
        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = [executor.submit(get_data, ll[i-1], ll[i], file, number_sensor,i) for i in range(1, len(ll))]

    elif type_file == "txt":
        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = [executor.submit(get_data_txt, file, ll[i - 1], ll[i], i) for i in range(1, len(ll))]

    with tqdm(total=(process*10)+10, file=sys.stdout, position=0, leave=True, desc="COSTRUCTION ARRAY") as pbar:
        array = create_np_array(number_sensor)
        pbar.update(10)
        ff = True
        if concurrent.futures.ALL_COMPLETED:
            for id in range(process):
                if ff:
                    array = np.append([array], results[id].result(), axis=0)
                    ff = False
                else:
                    array = np.append(array, results[id].result(), axis=0)
                pbar.update(10)
    return array


def create_table_txt(array,filename):
    np.savetxt("file_uploaded/"+filename, array, fmt='%s', delimiter='\t')
    print("created a file that contains data named: "+str(filename))
    return True


def create_pck_obj(array, filename):
    outfile = open("file_uploaded/"+filename, 'wb')
    pickle.dump(array, outfile)
    outfile.close()
    print("created a file pickle that contains data in a np array: " + str(filename))
    return True


def decrypte_pck_obj(infile):
    array = pickle.load(infile)
    infile.close()
    return array


def run(file, process, number_sensor, type_file):
    rn = random.randint(1, 10000)
    pathh = path+str(rn)+".txt"
    global file_log
    file_log = pathh
    sys.stdout = open(pathh, 'w')
    try:
        start = time.perf_counter()
        data_sens = add_result(file, process, number_sensor, type_file)
        finish = time.perf_counter()
        print(f'Finished in {round(finish-start,2)} second(s)')
    except Exception as e:
        print(e)
        data_sens = None

    sys.stdout.close()
    os.remove(pathh)
    sys.stdout = sys.__stdout__

    return data_sens