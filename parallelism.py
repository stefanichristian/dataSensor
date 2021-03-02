from multiprocessing import Pool
import numpy as np
import matplotlib.pyplot as plt
import scipy.io

filepathh =("APPA1.txt","APPA2.txt")

def get_table (filepath):
    file = open(filepath, "r")
    line = file.readline()
    first = True
    while line:
        # for i in range(3):
        word = ""
        list = []
        for c in line:
            if c == ',':
                list.append(word)
                word = ""
            else:
                word += c
        if first:
            m = np.array([list])
            first = False
        else:
            m = np.append(m, [list], axis=0)
        line = file.readline()
    return m


def pool_handler():
    p = Pool(2)
    p.map(get_table, filepathh)


if __name__ == '__main__':
    pool_handler()
    mat=scipy.io.loadmat('../Workspace_con_tutte_le_variabili.mat')
