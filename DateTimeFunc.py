import time
import datetime


def Get_Now_Date(dateFormat):

    nowDate = datetime.datetime.now()
    Y = nowDate.strftime("%Y")
    M = nowDate.strftime("%m")
    D = nowDate.strftime("%d")

    if dateFormat == "y-m-d":
        strDate = str(Y)+"-"+str(int(M))+"-"+str(int(D))
    elif dateFormat == "yyyy-mm-dd":
        strDate = str(Y)+"-"+str(M)+"-"+str(D)
    elif dateFormat == "yyyymmdd":
        strDate = str(Y)+str(M)+str(D)
    elif dateFormat == "yyyymmdd_HHMMSS":
        strDate = nowDate.strftime("%Y%m%d_%H%M%S")
    else:
        return 'Get_Now_Date("%s"),入参无效' % dateFormat

    return strDate


if __name__ == "__main__":
    print(Get_Now_Date("y-m-d"))
    print(Get_Now_Date("yyyy-mm-dd"))
    print(Get_Now_Date("yyyymmdd"))
    print(Get_Now_Date("yyyymmdd_HHMMSS"))

