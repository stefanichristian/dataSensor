import multiprocessing
import numpy as np

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
process = 16


# array_data=np.array([["Data"],["Data"],])


def set_proc_data(np, filepath):
    file = open(filepath, "r")
    file.seek(0, 2)
    filesz = file.tell()
    print("fsize: " + str(filesz))
    byte_for_proc = int(filesz / np)
    ll = []
    for _ in range(np):
        ll.append("")
    xx = data_for_proc_rec(byte_for_proc, np, file, 0, ll,filesz)
    print(xx)


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


set_proc_data(process, "appa2.log")
