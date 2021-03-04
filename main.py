import numpy as np
import matplotlib.pyplot as plt
import scipy.io

def getTable (filepath):
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

#mat=scipy.io.loadmat('../Workspace_con_tutte_le_variabili.mat')

appa1=getTable("APPA1.txt")
print(appa1[:, 1])
#appa2=getTable("APPA2.txt")

#print(mat["R3_appa2"][4])

#print(appa2[0][0])





