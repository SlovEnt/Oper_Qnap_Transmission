# -*- coding: utf-8 -*-
__author__ = 'SlovEnt'
__date__ = '2018/4/28 21:36'
__version__ = '1.1'


from datetime import datetime
import os
import re
import time

def Get_Now_Date(dateFormat):

    nowDate = datetime.now()
    Y = nowDate.strftime("%Y")
    M = nowDate.strftime("%m")
    D = nowDate.strftime("%d")

    if dateFormat == "y-m-d" or dateFormat == "Y-M-D":
        strDate = str(Y)+"-"+str(int(M))+"-"+str(int(D))
    elif dateFormat == "yyyy-mm-dd" or dateFormat == "YYYY-MM-DD":
        strDate = str(Y)+"-"+str(M)+"-"+str(D)
    elif dateFormat == "yyyymmdd" or dateFormat == "YYYYMMDD":
        strDate = str(Y)+str(M)+str(D)
    elif dateFormat == "yyyymmdd_HHMMSS" or dateFormat == "YYYYMMDD_HHMMSS":
        strDate = nowDate.strftime("%Y%m%d_%H%M%S")
    else:
        return 'Get_Now_Date("%s"),入参无效' % dateFormat

    return strDate

def Get_Param_Info(ConfigFile):

    if os.path.isfile(ConfigFile) == False:
        raise Exception("错误，全局参数配置文件不存在")

    paramInfo = {}
    for line in open(ConfigFile,"r",encoding= 'UTF-8'):
        if line != "\n" :
            info = line.strip("\n")
            # 首字符为 # ; 等符号 视为注释
            if info.strip()[0] != "#" and info.strip()[0] != ";" and info.strip()[0] != "[" :
                # print(info.strip()[0])
                info = info.split("=")
                if len(info) == 2:
                    paramName = info[0].strip()
                    paramValue = info[1].strip()
                    paramInfo[paramName] = paramValue
    return paramInfo

def Dict2List(dic:dict):
    ''' 将字典转化为列表 '''
    keys = dic.keys()
    vals = dic.values()
    lst = [(key, val) for key, val in zip(keys, vals)]
    return lst

def Comp_MultilineText(multStr):
    ''' 压缩多行文本代码，主要用于多行SQL压缩为一行 '''
    line = multStr.splitlines()
    ''' 如果行数不仅仅只为一行，则进行多行处理模式 '''
    if len(line) != 1 :
        newSql = ""
        for x in line:
            newSql = newSql + " " + x.lstrip()
            newSql = re.sub(r'\s{2,}',' ',newSql)
        return newSql.lstrip().rstrip()
    else:
        ''' 单行只需要去除前后空格即可 '''
        return multStr.lstrip().rstrip()

def Get_Trading_Day():
    # 获取交易日,通过组策略下发的文本文件
    todayYMD = time.strftime("%Y%m%d", time.localtime())  # YYYYMMDD
    tradeDayFile = r"C:\Windows\HolidayList.txt"
    fileRdade = open(tradeDayFile)
    line = fileRdade.readline()
    while line:
        strFlag = line.split(" ")
        if todayYMD == strFlag[0] and int(strFlag[1]) == 2:
            return False
        line = fileRdade.readline()
    fileRdade.close()
    return True

def Get_Last_Trading_Day(dfDay):
    # 获取交易日,通过组策略下发的文本文件取上一个交易日

    nowDay = datetime.datetime.now()

    deltaDayNum = int(dfDay)

    ''' 日历由域控下发，不在域控的机器需要手工拷贝文件到该目录 '''
    tradeDayFile = r"C:\Windows\HolidayList.txt"
    fileRdade = open(tradeDayFile)

    dayFlagArr = []
    for line in fileRdade.readlines():
        ''' 合并字典日期和节假日标志，保持为无空格字符串用于匹配比对 '''
        dayFlag = line.strip("\n").replace(" ", "")
        dayFlagArr.append(dayFlag)

    while True :

        ''' 日期计算 得出指定的上一个交易日 '''
        deltaDay = datetime.timedelta(days=deltaDayNum)
        lastTradeDay = nowDay - deltaDay
        lastTradeDayX = lastTradeDay.strftime('%Y%m%d')
        lastTradeDay = "%s1" % lastTradeDay.strftime('%Y%m%d') # YYYYMMDDF F=标志（1或2）

        if lastTradeDay in dayFlagArr:
            ''' 如果计算出的交易日加标识包含在数组内，则认为当前日期为交易日 '''
            return lastTradeDayX
        elif deltaDayNum > 365 :
            ''' 如果循环日期超过365次，不可能会出现连续放假365天的可能，则基本认为是交易日历有问题 '''
            return False

        ''' 如果是非交易日，则计数累计加1 取再上一天 '''
        deltaDayNum = deltaDayNum + 1

    return False

def Print_Dict_KandV(dict,dictName="x"):
    for key, value in dict.items():
        print ("""{2}["{0}"] = {1}""".format(key, value, dictName))
    print()
    time.sleep(0.5)

