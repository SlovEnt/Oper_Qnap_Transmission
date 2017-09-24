import os
import re
import pymysql
from Comm_Func import *
from Oper_Mysql_Class import *

paramInfo = Get_Param_Info(configFile)
dbHost = paramInfo["DB_HOST"]
dbPort = int(paramInfo["DB_PORT"])
dbName = paramInfo["DB_NAME"]
dbUser = paramInfo["USER_NAME"]
dbPasswd = paramInfo["USER_PWD"]
mysqlConn = pymysql.connect(host=dbHost, user=dbUser, password=dbPasswd, database=dbName, port=dbPort, charset="utf8")
dbCursor = mysqlConn.cursor()

if __name__ == "__main__":
    # 网络共享路径
    rootDir = r"\\192.168.1.201\Datas\Bad_Item\temp\磁力搜合集\磁力搜合集1"
    for strRoot, lsDir, lsFiles in os.walk(rootDir):
        for strFile in lsFiles:
            singFullPathFileExt = os.path.join(strRoot, strFile)
            # print(singFullPathFileExt)
            fileObject=open(singFullPathFileExt,'r')
            content=[]
            for eachline in fileObject:
                strLine = "<mg>%s<mg>" % eachline.strip()
                if "magnet" in strLine:
                    # print(debug(),strLine)

                    # dataReg0 = re.compile(r'''<mg>magnet:\?xt=urn:btih:(.+?)&amp;dn=(.+?)<mg>''')
                    magnetDatas1 = re.compile(r'''<mg>magnet:\?xt=urn:btih:(.+?)&(.+?)<mg>''').findall(strLine)
                    magnetDatas0 = re.compile(r'''<mg>magnet:\?xt=urn:btih:(.+?)&dn=(.+?)<mg>''').findall(strLine)
                    magnetDatas2 = re.compile(r'''<mg>magnetxt=(.+?)&dn=(.+?)<mg>''').findall(strLine)
                    magnetDatas3 = re.compile(r'''<mg>magnet:\?xt=urn:btih:(.+?)<mg>''').findall(strLine)
                    if len(magnetDatas0) != 0:
                        for x in magnetDatas0 :
                            # print(tmpinfo(), strLine, x)
                            strSql = "select count(1) from get_tpb_all_magnet where hash_string = '%s';" % (x[0])
                            dbCursor.execute(strSql.encode('utf-8'))
                            rtnCnt = dbCursor.fetchall()[0][0]
                            if rtnCnt == 0 :
                                insertSQL = "INSERT INTO get_tpb_all_magnet (up_datetime, hash_string, up_user, rs_name, rs_category, rs_type, up_size, magnet, down_flag) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (
                                    "2016-01-01 00:00:00", x[0], "SEX169", strFile + " " + x[1], "Porn", "Movies", "-", strLine.replace("<mg>",""), "0"
                                )
                                print(debug(), "%s" % (insertSQL))
                                dbCursor.execute(strSql.encode('utf-8'))
                    elif len(magnetDatas1) != 0:
                        for x in magnetDatas1 :
                            # print(tmpinfo(), strLine, x)
                            strSql = "select count(1) from get_tpb_all_magnet where hash_string = '%s';" % (x[0])
                            dbCursor.execute(strSql.encode('utf-8'))
                            rtnCnt = dbCursor.fetchall()[0][0]
                            if rtnCnt == 0 :
                                insertSQL = "INSERT INTO get_tpb_all_magnet (up_datetime, hash_string, up_user, rs_name, rs_category, rs_type, up_size, magnet, down_flag) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (
                                    "2016-01-01 00:00:00", x[0], "SEX169", strFile + " " + x[1], "Porn", "Movies", "-", strLine.replace("<mg>",""), "0"
                                )
                                print(debug(), "%s" % (insertSQL))
                                dbCursor.execute(strSql.encode('utf-8'))
                    elif len(magnetDatas2) != 0:
                        for x in magnetDatas2 :
                            strSql = "select count(1) from get_tpb_all_magnet where hash_string = '%s';" % (x[0])
                            dbCursor.execute(strSql.encode('utf-8'))
                            rtnCnt = dbCursor.fetchall()[0][0]
                            if rtnCnt == 0:
                                insertSQL = "INSERT INTO get_tpb_all_magnet (up_datetime, hash_string, up_user, rs_name, rs_category, rs_type, up_size, magnet, down_flag) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (
                                    "2016-01-01 00:00:00", x[0], "SEX169", strFile + " " + x[1], "Porn", "Movies", "-",
                                    strLine.replace("<mg>", ""), "0"
                                )
                                print(debug(), "%s" % (insertSQL))
                                dbCursor.execute(strSql.encode('utf-8'))
                    elif len(magnetDatas3) != 0:
                        for x in magnetDatas3 :
                            strSql = "select count(1) from get_tpb_all_magnet where hash_string = '%s';" % (x)
                            dbCursor.execute(strSql.encode('utf-8'))
                            rtnCnt = dbCursor.fetchall()[0][0]
                            if rtnCnt == 0:
                                insertSQL = "INSERT INTO get_tpb_all_magnet (up_datetime, hash_string, up_user, rs_name, rs_category, rs_type, up_size, magnet, down_flag) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (
                                    "2016-01-01 00:00:00", x, "SEX169", strFile, "Porn", "Movies", "-",
                                    strLine.replace("<mg>", ""), "0"
                                )
                                print(debug(), "%s" % (insertSQL))
                                dbCursor.execute(strSql.encode('utf-8'))
                    else:
                        print(tmpinfo("XWX"), singFullPathFileExt, strLine)


                    # if len(magnetDatas0) != 0:
                    #     for x in magnetDatas0:
                    #         print(tmpinfo(),strLine,x)
                    # elif len(magnetDatas1) != 0:
                    #     # print(tmpinfo("magnetDatas1"),strLine)
                    #     for x in magnetDatas1:
                    #         print(tmpinfo(),strLine,x)
                    # elif len(magnetDatas2) != 0:
                    #     for x in magnetDatas1:
                    #         print(tmpinfo(),strLine,x)

                    # else:
                        # print(debug(),strLine)
                        # pass
                    # print(singFullPathFileExt)
                    # print(strFile.replace(".txt",""),strLine)












