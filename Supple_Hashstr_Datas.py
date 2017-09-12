import re
import datetime
import math
from PrintFormatLogs import *
from Oper_Mysql_Class import *


def __Add_DB_HashString(recNum, magnet, rs_name):

    dataReg = re.compile(r'''magnet:\?xt=urn:btih:(.+?)&amp;dn''')
    hash_string = dataReg.findall(magnet)[0]

    strSql = "update get_tpb_all_magnet set hash_string = '%s' where rs_name = '%s'" % (hash_string, rs_name)
    mysqlExe.ExecNonQuery(strSql.encode('utf-8'))
    print(debug(), recNum, strSql)


if __name__ == "__main__":

    strSql = "SELECT COUNT(*) FROM get_tpb_all_magnet where hash_string='';"
    rtnCnt = mysqlExe.ExecQuery(strSql.encode('utf-8'))[0][0]

    suffix = math.ceil(rtnCnt/100)
    recNum = 0

    for i in range(0, suffix):
        print(debug(), "一共需要修改 %s 条记录，本次为第 %s 次循环！！！！！" % (rtnCnt, i + 1))
        strSql = "SELECT hash_string,rs_name,magnet FROM get_tpb_all_magnet where hash_string='' LIMIT %s ;" % (100)
        rtnDatas = mysqlExe.ExecQuery(strSql.encode('utf-8'))

        for x in rtnDatas:
            recNum += 1
            rs_name = x[1].replace("'","''")
            magnet = x[2]

            dataReg = re.compile(r'''magnet:\?xt=urn:btih:(.+?)&amp;dn''')

            if len(dataReg.findall(magnet)) != 0 :
                hash_string = dataReg.findall(magnet)[0]

                strSql = "update get_tpb_all_magnet set hash_string = '%s' where rs_name = '%s'" % (hash_string, rs_name)
                mysqlExe.ExecNonQuery(strSql.encode('utf-8'))
                print(debug(), recNum, strSql)

            else:
                strSql = "delete from get_tpb_all_magnet where magnet = '%s'" % (magnet)
                mysqlExe.ExecNonQuery(strSql.encode('utf-8'))
                print(debug(), recNum, strSql)

    # for i in range(0, suffix):
    #
    #     print(debug(), "一共需要修改 %s 条记录，本次为第 %s 次循环！！！！！" % (rtnCnt, i+1))
    #
    #     # strSql = "SELECT hash_string,rs_name,magnet FROM get_tpb_all_magnet where hash_string='' LIMIT %s, %s;" % (100*i,100*i+100)
    #     strSql = "SELECT hash_string,rs_name,magnet FROM get_tpb_all_magnet where hash_string='' LIMIT %s ;" % (100)
    #     rtnDatas = mysqlExe.ExecQuery(strSql.encode('utf-8'))
    #
    #     p = Pool(5)
    #
    #     for x in rtnDatas:
    #
    #         recNum += 1
    #         rs_name = x[1]
    #         magnet = x[2]
    #
    #         p.apply_async(__Add_DB_HashString, args=(recNum, magnet, rs_name))
    #
    #     p.close()
    #     p.join()
    #
    #     rtnCnt -= 100
