import os
import time

import pymysql

import paramiko
import hashlib
import math

from Comm_Func import *
from Oper_Mysql_Class import *


def __Get_File_MD5(singFile):

    # 大文件上限 超过此大小限制 则认为是大文件
    _FILE_SLIM = 100 * 1024 * 1024

    # md5sum SEX169所有域名如下.txt|cut -d ' ' -f1
    calltimes = 0  # 分片的个数

    myhash = hashlib.md5()
    f = open(singFile,"rb")
    f_size = os.stat(singFile).st_size  # 得到文件的大小
    if f_size > _FILE_SLIM:
        while (f_size > _FILE_SLIM):
            myhash.update(f.read(_FILE_SLIM))
            f_size /= _FILE_SLIM
            calltimes += 1  # delete    #文件大于100M时进行分片处理
        if (f_size > 0) and (f_size <= _FILE_SLIM):
            myhash.update(f.read())
    else:
        myhash.update(f.read())

    f.close()
    return myhash.hexdigest()

def __Get_SSH_Hander(nasHost,nasPort,nasUser,nasPasswd):
    sshCmd = paramiko.SSHClient()
    sshCmd.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshCmd.connect(nasHost, nasPort, nasUser, nasPasswd)
    return sshCmd

def __Linux_File_MD5(sshCmd,fileName):
    strCMD = '''md5sum "%s"|cut -d ' ' -f1''' % fileName
    stdin, stdout, stderr = sshCmd.exec_command(strCMD)
    rtnMsg = stdout.readline().strip("\n")
    return rtnMsg

def __Linux_ExecCMD(sshCmd,strCMD):
    # print(debug(),"执行命令：%s" % strCMD)
    stdin, stdout, stderr = sshCmd.exec_command(strCMD)
    for std in stdout.readlines():
        # print(debug(),"命令返回结果为：%s；" % std.strip("\n"))
        return std.strip("\n")

def __Insert_PathFiles_DB(dbCursor, rootDir, remoteRootDir) :

    for strRoot, lsDir, lsFiles in os.walk(rootDir):

        for strFile in lsFiles:

            singFullPathFileExt = os.path.join(strRoot, strFile)
            remotePathFile = singFullPathFileExt.replace(rootDir, remoteRootDir).replace("\\", "/").replace("'", "''")
            netPathFile = singFullPathFileExt.replace(r"\\", "\\\\").replace("'", "''")
            strFile = strFile.replace("'", "''")

            strSql = "select count(*) from nas_files where remote_path_file = '%s' ;" % (remotePathFile)
            dbCursor.execute(strSql.encode('utf-8'))
            rtnCnt = dbCursor.fetchall()[0][0]

            if rtnCnt == 0:
                strSql = "INSERT INTO nas_files (remote_path_file, net_path_file,file_name) VALUES ('%s','%s','%s');" % (
                remotePathFile, netPathFile.replace("\\","\\\\"), strFile)
                print(tmpinfo(), strSql)
                dbCursor.execute(strSql.encode('utf-8'))
            else:
                print(tmpinfo(),"%s 已存在！！！！" % singFullPathFileExt)


if __name__ == "__main__":

    print()

    # print(__Get_File_MD5(r"\\192.168.1.201\Datas\Bad_Item\XM_Transmission\Aspen Ora - Hard - anal sex in my bathroom with my man.mp4"))

    paramInfo = Get_Param_Info(configFile)
    dbHost = paramInfo["DB_HOST"]
    dbPort = int(paramInfo["DB_PORT"])
    dbName = paramInfo["DB_NAME"]
    dbUser = paramInfo["USER_NAME"]
    dbPasswd = paramInfo["USER_PWD"]
    mysqlConn = pymysql.connect(host=dbHost, user=dbUser, password=dbPasswd, database=dbName, port=dbPort, charset="utf8")
    dbCursor = mysqlConn.cursor()

    paramInfo = Get_Param_In_DB("QNAP_NAS")
    nasHost = paramInfo["NAS_HOST"]
    nasPort = int(paramInfo["NAS_PORT"])
    nasUser = paramInfo["NAS_USER"]
    nasPasswd = paramInfo["NAS_PASSWD"]
    sshCmd = __Get_SSH_Hander(nasHost,nasPort,nasUser,nasPasswd)

    print(debug(),nasHost,nasPort,nasUser,"********")
    print()

    try:

        # 网络共享路径
        rootDir = r"\\192.168.1.201\Datas\Bad_Item"

        # 远程实际路径
        remoteRootDir = r"/share/CACHEDEV1_DATA/Datas/Bad_Item"

        _RTN_ROW = 100

        # __Insert_PathFiles_DB(dbCursor, rootDir, remoteRootDir)

        strSql = "select count(*) from nas_files where md5_string = '' or md5_string is null;"
        dbCursor.execute(strSql.encode('utf-8'))
        rtnCnt = dbCursor.fetchall()[0][0]
        print(debug(),"获取要处理的文件总数为 %s" % rtnCnt)

        if rtnCnt != 0:
            rtnUpperLimit = math.ceil(int(rtnCnt) / _RTN_ROW)

            for i in range(1,rtnUpperLimit+1):

                strSql = "select remote_path_file from nas_files where md5_string = '' or md5_string is null limit %s;" % _RTN_ROW
                dbCursor.execute(strSql.encode('utf-8'))
                rtnDatas = dbCursor.fetchall()
                print()
                print(debug(),"正在进行第 %d 次处理！" % i)

                for x in rtnDatas :
                    fileName = x[0]
                    # print(debug(),"处理文件 %s ！" % fileName)
                    strCMD = '''md5sum "%s"|cut -d ' ' -f1''' % fileName
                    md5Code = __Linux_ExecCMD(sshCmd, strCMD)
                    strSql = "select count(*) from nas_files where md5_string = '%s' and  remote_path_file <> '%s' ;" % (md5Code,fileName)
                    dbCursor.execute(strSql.encode('utf-8'))
                    rtnCnt = dbCursor.fetchall()[0][0]
                    if rtnCnt == 0:
                        repeatFlag = "0"
                    else:
                        repeatFlag = "1"
                    strSql = "update nas_files set md5_string = '%s',repeat_flag = '%s' where remote_path_file = '%s';" % (md5Code, repeatFlag, fileName)
                    print(debug(),strSql)
                    dbCursor.execute(strSql.encode('utf-8'))
        # else:
        #     pass







                # singFullPathFileExt = os.path.join(strRoot,strFile)
                # # print(debug(),__Get_File_MD5(singFullPathFileExt),strRoot,strFile)
                #
                # convRootPath = strRoot.replace(r"\\","\\\\")
                # convRootPath = strRoot.replace(r"'","''")
                # strFile = strFile.replace("'","''")
                #
                # singFullPathFileExt = singFullPathFileExt.replace(r"\\","\\\\")
                # singFullPathFileExt = strRoot.replace(r"'","''")
                # print(singFullPathFileExt)

                # # strSql = "select count(*) from nas_files where `all_path` = '%s' and `file_name` = '%s' and  `md5_string` = '%s' ;" % (convRootPath.replace("\\","\\\\"), strFile, __Get_File_MD5(singFullPathFileExt))
                # strSql = "select count(*) from nas_files where `all_path` = '%s' and `file_name` = '%s' ;" % (convRootPath.replace("\\","\\\\"), strFile )
                # # print(debug(),strSql)
                # rtnCnt = mysqlExe.ExecQuery(strSql.encode('utf-8'))[0][0]
                # if rtnCnt == 0:
                #     strSql = "select count(*) from nas_files where `md5_string` = '%s' ;" % (__Get_File_MD5(singFullPathFileExt))
                #     rtnCnt = mysqlExe.ExecQuery(strSql.encode('utf-8'))[0][0]
                #     if rtnCnt != 0:
                #         repeat_flag = 1 # 已存在相同文件
                #     else:
                #         repeat_flag = 0
                #     strSql = "INSERT INTO nas_files (path_file, `all_path`, `file_name`, `md5_string`, repeat_flag) VALUES ('%s','%s', '%s', '%s', '%s');" % (singFullPathFileExt, convRootPath.replace("\\","\\\\"), strFile, __Get_File_MD5(singFullPathFileExt),repeat_flag)
                #     print(debug(),strSql)
                #     mysqlExe.ExecNonQuery(strSql.encode('utf-8'))
                # else:
                #     print(debug(), r"跳过 %s" % (singFullPathFileExt))

    except Exception as e:
        print (errinfo(),strSql)
        print (errinfo(),e)




