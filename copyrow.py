file = open("appa2.log","r")
fileaa = open("aa.txt","w+")

for _ in range(250000):
    fileaa.write(file.readline())
file.close()
fileaa.close()