# -*- coding: utf-8 -*-
__author__ = 'SlovEnt'
__date__ = '2018/5/31 21:35'

import os


FILE_PATH = r"\\192.168.31.201\Datas\Bad_Item\99_Classify\Fansadox Collection"

fileArr = []
list = os.listdir(FILE_PATH) #列出文件夹下所有的目录与文件
for i in range(0,len(list)):

    fileNum = list[i][20:23]
    print(fileNum, list[i])

    fileArr.append(fileNum)

    # path = os.path.join(FILE_PATH,list[i])
    # if os.path.isfile(path):
    #     print(path)

# print(fileArr)
print()

for x in range(1, 491+1):
    ifNum = "%03d" % x

    if ifNum not in fileArr:
        print(ifNum)





