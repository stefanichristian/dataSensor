import concurrent.futures
import numpy as np
import time
import pickle

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
mouths = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
id_process = 1 #id of start process


def set_proc_data(np, filepath,number_process):
    file = open(filepath, "r")
    file.seek(0, 2)
    filesz = file.tell()
    byte_for_proc = int(filesz / np)
    ll = []
    for _ in range(np):
        ll.append("")
    print("file size: " + str(filesz))
    print("byte_min_proc: " + str(byte_for_proc))
    print("expected number of process: "+str(number_process))
    list_read_byte = data_for_proc_rec(byte_for_proc, np, file, 0, ll, filesz)
    file.close()
    return list_read_byte


def data_for_proc_rec(byte, num_p, file, id_proc, list, filesz):
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
    #print("for_p: " + str(file.tell()))
    ex = False
    line = "asd"
    while not ex and line:
        line = file.readline()
        #print("line: "+line)
        for word in line.split():
            if word in days:
                #print("w at: " + str(file.tell() - len(line)))
                list[id_proc] = file.tell() - len(line)
                ex = True
    return data_for_proc_rec(byte, num_p, file, id_proc + 1, list, filesz)

def create_np_array(number_sens):
    x = np.array([["Data"]])
    for id in range(number_sens):
        x = np.append(x, [["Risc_"+str(id+1)], ["Signal_"+str(id+1)], ["Volt_"+str(id+1)]])
    x = np.append(x, [["Temp"], ["Rh%"]])
    return x


def type_line(line):
    word = line[0:3]
    if word == '':
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
    if line == '':
        return -1
    for word in line.split():
        if word in days:
            return 0
        elif word[0] == 'S' and  word[1].isnumeric() and word[2].isnumeric():
            return 1
        elif word[0] == 'T' and word[1] == ':':
            return 2
        else:
            return -1
    return -1                                       #non itera se la riga è vuota, ma il primo if non funziona boh

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
        elif tp == -1:               #end of file or end data
            exit = True
    return supp_list


def get_data(start, end, filepath, number_sens, id_process):
    print("process created with id: "+str(id_process)+", read_byte from "+str(start)+" to "+str(end))
    file = open(filepath, "r")
    firsttime = True
    thereisdata = False
    file.seek(start, 0)
    seek = start
    list = []
    while seek < end:
        line = file.readline()
        tp = type_line(line)
        if tp == -1:
            tp = is_broken_line(line)
        if tp == 0:
            first_byte_mis = int(file.tell())-len(line)
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
        else:
            if thereisdata and len(list) != (number_sens*3)+3:
                list = recovery_list(file, first_byte_mis, number_sens)
            if thereisdata and firsttime:
                thereisdata = False
                array_data = np.array([list], dtype=str)
                firsttime = False
            elif thereisdata:
                thereisdata = False
                array_data = np.append(array_data, [list], axis=0)
        seek = file.tell()
    file.close()
    return array_data


def add_result(pathname, process, number_sensor):
    ll = set_proc_data(process, pathname, process)
    ll.insert(0,0)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = [executor.submit(get_data, ll[i-1], ll[i], pathname, number_sensor,i) for i in range(1, len(ll))]

    array = create_np_array(number_sensor)
    ff = True
    if concurrent.futures.ALL_COMPLETED:
        for id in range(process):
            if ff:
                array = np.append([array], results[id].result(), axis=0)
                ff = False
            else:
                array = np.append(array, results[id].result(), axis=0)
    return array


def create_table_txt(array,filename):
    np.savetxt(filename, array, fmt='%s')
    print("created a file that contains data named: "+str(filename))
    return True


def create_pck_obj(array, filename):
    outfile = open(filename, 'wb')
    pickle.dump(array, outfile)
    outfile.close()
    print("created a file pickle that contains data in a np array: " + str(filename))
    return True

# data_sens = add_result()
"""
print("Hello, which file do you want analyze?")
pathname = input("Write name with extension ex-> data.log\n") or "aa.txt"
process = int(input("How many process do you want create?\n") or "8")
number_sensor = int(input("How many sensor do you have?\n") or "8")
"""
def run(pathname, process, number_sensor):
    start = time.perf_counter()
    data_sens = add_result(pathname, process, number_sensor)
    # data_sens = add_result("file_uploaded/aa.txt", 8, 8)
    finish = time.perf_counter()
    print(f'Finished in {round(finish-start,2)} second(s)')
    choose = input("Digits \"1\" for create a file txt or \"2\" to save the np array as pickle file or \"Q\" to quit\n")
    if choose == "1":
        name = input("Name file?\n") or "datisensori.txt"
        create_table_txt(data_sens, name)
    if choose == "2":
        name = input("Name file?\n") or "datisensori"
        create_pck_obj(data_sens, name)
    return True