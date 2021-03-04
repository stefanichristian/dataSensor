from multiprocessing import Pool
import numpy as np
import matplotlib.pyplot as plt
import scipy.io

filepathh =("APPA1.txt","APPA2.txt")

def get_table (filepath):
    file = open(filepath, "r")
    line = file.readline()
    x=file.tell()
    print(line)
    print(x)
    file.seek(0,2)
    x=file.tell()
    print(x)
    file.seek(0,0)
    print(file.tell())


get_table("web_app/example/aa.txt")


