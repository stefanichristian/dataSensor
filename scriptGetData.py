import concurrent.futures
import numpy as np
import time

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
mouths = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
process = 4
number_sensor = 8
pathname = "aa.txt"
id_process = 1

# array_data=np.array([["Data"],["Data"],])


def set_proc_data(np, filepath):
    file = open(filepath, "r")
    file.seek(0, 2)
    filesz = file.tell()
    byte_for_proc = int(filesz / np)
    ll = []
    for _ in range(np):
        ll.append("")
    print("fsize: " + str(filesz))
    print("byte_min_proc: " + str(byte_for_proc))
    xx = data_for_proc_rec(byte_for_proc, np, file, 0, ll,filesz)
    file.close()
    print(xx)
    return xx

"""
def data_for_proc(byte, np, file):
    list = [byte]
    file.seek(byte, 0)
    #print("for_p: " + str(file.tell()))
    ex = False
    while not ex:
        line = file.readline()
        for word in line.split():
            if word in days:
                print("w at: " + str(file.tell() - len(line)))
                list[0] = file.tell() - len(line)
                ex = True
    file.seek(list[0], 0)
"""


def data_for_proc_rec(byte, num_p, file, id_proc, list, filesz):
    #print("call: byte "+str(byte)+", num_p "+str(num_p)+", id_proc "+str(id_proc)+", list "+str(list))
    if id_proc == 0:
        file.seek(byte, 0)
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
        if save:
            str += " "+word
        if "GMT" in word:
            save = False
    return str

def recovery_list(n):
    pass
    #print("recovery list")


def get_data(start, end, filepath, number_sens,id_process):
    print("process created, id: "+str(id_process))
    file=open(filepath, "r")
    firsttime = True
    file.seek(start, 0)
    seek = start
    list = []
    while seek < end:
        line = file.readline()
        tp = type_line(line)
        if tp == 0:
            #print(list)
            list = []
            list.append(take_datatime(line))
        elif tp == 1:
            sens_data = line.split(":")
            #print("sens_data: "+str(sens_data))
            for id in range(3):
                list.append(float(sens_data[id+1]))
        elif tp == 2:
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
                recovery_list(number_sens)
            else:
                if firsttime:
                    array_data = np.array([list], dtype=str)
                    firsttime= False
                else:
                    array_data = np.append(array_data, [list],axis=0)
        else:
            pass
            #print("len: "+str(len(list)))
            #print("table: "+str(array_data))
            #print("All Good!")
        seek = file.tell()
    file.close()
    return array_data
    #print("table:"+str(array_data))#
    #print("first row: "+str(array_data[0][19])+ " type: "+str(type(array_data[0][1])))


def add_result():
    ll = set_proc_data(process, "aa.txt")
    ll.insert(0,0)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = [executor.submit(get_data, ll[i-1], ll[i], "aa.txt", number_sensor,i) for i in range(1, len(ll))]

    array = create_np_array(number_sensor)
    ff = True
    for f in concurrent.futures.as_completed(results):
        if ff:
            array = np.append([array], f.result(), axis=0)
            ff = False
        else:
            array = np.append(array, f.result(), axis=0)
        print(array)


    #array = np.append([array], xx, axis=0)
    #print(array)
    np.savetxt("ciccio.txt",array, fmt='%s')


#create_np_array(8)
start = time.perf_counter()
add_result()
#xx = get_data(0, 3067992, "aa.txt", number_sensor,1)
finish = time.perf_counter()
print(f'Finished in {round(finish-start,2)} second(s)')


#get_data(0,18372,"aa.txt", number_sensor)
