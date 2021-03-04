import concurrent.futures
import numpy as np
import time
import pickle

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
mouths = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
process = 1
number_sensor = 8
pathname = "aa.txt" #file where you read the data
id_process = 1 #id of start process


def set_proc_data(np, filepath):
    file = open(filepath, "r")
    file.seek(0, 2)
    filesz = file.tell()
    byte_for_proc = int(filesz / np)
    ll = []
    for _ in range(np):
        ll.append("")
    print("file size: " + str(filesz))
    print("byte_min_proc: " + str(byte_for_proc))
    print("expected number of process: "+str(process))
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
    #print(x)
    return x


def type_line(line):
    word = line[0:3]
    #print("line: "+str(line))
    if word == '':
        print("end of file")
        return 3
    elif word in days:
        print("line: 0: " + str(line))
        return 0
    elif word[0] == 'S' and  word[1].isnumeric() and word[2].isnumeric():
        print("line: 1: " + str(line))
        return 1
    elif word[0] == 'T' and word[1] == ':':
        print("line: 2: " + str(line))
        return 2
    else:
        print("line: -1: " + str(line))
        return -1

def is_broken_line(line):
    for word in line.split():
        if word in days:
            return 0
        elif word[0] == 'S' and  word[1].isnumeric() and word[2].isnumeric():
            return 1
        elif word[0] == 'T' and word[1] == ':':
            return 2
        else:
            return -1

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


def recovery_list(file, start_byte):
    exit = False
    file.seek(start_byte, 0)
    supp_list = []
    for _ in range((number_sensor * 3) + 3):
        supp_list.append("NaN")
    while not exit:
        line = file.readline()
        #print("line: "+line)
        tp = type_line(line)
        if tp == -1:
            if is_broken_line(line) == 0:
                tp = 0
            elif is_broken_line(line) == 1:
                tp = 1
            elif is_broken_line(line) == 2:
                tp = 2
            else:
                pass
        if tp == 0:
            supp_list[0]= take_datatime(line)
        elif tp == 1:
            sens_data = line.split(":")
            # print("sens_data: "+str(sens_data))
            for id in range(3):
                supp_list[(((int(sens_data[0][1]))-1)*3)+1+id] = (float(sens_data[id + 1]))
        elif tp == 2:
            sens_data = line.split(":")
            # print("sens_data: "+str(sens_data))
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
        elif tp == 3 or tp == -1:               #end of file
            exit = True
    print("exit rec")
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
            if is_broken_line(line) == 0:
                tp = 0
            elif is_broken_line(line) == 1:
                tp = 1
            elif is_broken_line(line) == 2:
                tp = 2
            else:
                tp = -1
        if tp == 0:
            #print(list)
            first_byte_mis = int(file.tell())-len(line)
            thereisdata = True
            list = []
            list.append(take_datatime(line))
        elif tp == 1:
            thereisdata = True
            sens_data = line.split(":")
            #print("sens_data: "+str(sens_data))
            for id in range(3):
                list.append(float(sens_data[id+1]))
        elif tp == 2:
            thereisdata = True
            gen_data = line.split(":")
            # print("sens_data: "+str(sens_data))
            take = False
            for w in gen_data:
                if take:
                    list.append(float(w))
                    take = False
                if "T" == w or "H" == w:
                    take = True
            if len(list) != (number_sens*3)+3:
                thereisdata = False
                list = recovery_list(file, first_byte_mis)
            if firsttime:
                array_data = np.array([list], dtype=str)
                firsttime= False
                thereisdata = False
            else:
                thereisdata = False
                array_data = np.append(array_data, [list], axis=0)
        else:
            if thereisdata and len(list) != (number_sens*3)+3:
                thereisdata = False
                print("enter")
                list = recovery_list(file, first_byte_mis)
                if firsttime:
                    print("insert")
                    array_data = np.array([list], dtype=str)
                    firsttime = False
                else:
                    print("insert")
                    array_data = np.append(array_data, [list], axis=0)
        seek = file.tell()
    file.close()
    #print("finish")
    return array_data


def add_result():
    ll = set_proc_data(process, pathname)
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


def create_pck_obj(array):
    filename = 'data_sensor_gas'
    outfile = open(filename, 'wb')
    pickle.dump(array, outfile)
    outfile.close()
    print("created a file pickle that contains data in a np array: " + str(filename))
    return True


start = time.perf_counter()
data_sens = add_result()
#print("DIO: "+str(data_sens[:,1]))
create_table_txt(data_sens, "datisensori.txt")
#xx = get_data(0, 3067992, pathname, number_sensor,1)
finish = time.perf_counter()
print(f'Finished in {round(finish-start,2)} second(s)')


#get_data(0,18372,"pathname, number_sensor)
