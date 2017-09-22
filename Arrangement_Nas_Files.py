import os
import time
from builtins import int

import paramiko
import hashlib

from Comm_Func import *
from Oper_Mysql_Class import *


def __Get_File_MD5(singFile):

    # md5sum SEX169所有域名如下.txt|cut -d ' ' -f1
    myhash = hashlib.md5()
    f=open(singFile,"rb")
    while True:
        b=f.read(8096)
        if not b:
            break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()

def __Get_SSH_Hander(nasHost,nasPort,nasUser,nasPasswd):
    sshCmd = paramiko.SSHClient()
    sshCmd.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshCmd.connect(nasHost, nasPort, nasUser, nasPasswd)
    return sshCmd

def __Linux_File_MD5(sshCmd,fileName):
    strCMD = '''md5sum %s|cut -d ' ' -f1''' % fileName
    stdin, stdout, stderr = sshCmd.exec_command(strCMD)
    rtnMsg = stdout.readline().strip("\n")
    return rtnMsg

def __Linux_ExecCMD(sshCmd,strCMD):
    print(debug(),"执行命令：%s；" % strCMD)
    stdin, stdout, stderr = sshCmd.exec_command(strCMD)
    for std in stdout.readlines():
        # print(debug(),"命令返回结果为：%s；" % std.strip("\n"))
        return std.strip("\n")


def __Ssh_Login_Nas(nasHost,nasPort,nasUser,nasPasswd):

    try:
        sshTran = paramiko.Transport(nasHost, nasPort)
        sshTran.connect(username=nasUser, password=nasPasswd)
        chan = sshTran.open_session()
        # chan.settimeout(60)
        # chan.get_pty()
        # chan.invoke_shell()
        # # sendCmd = "rsync -av --progress /userdisk/data/transmission/downloads/.  admin@192.168.1.201:/share/Datas/Bad_Item/XM_Transmission/%s" % ("NEW_"+ str("%06d") % fld)
        # sendCmd = "rsync -av --progress /userdisk/data/transmission/downloads/.  admin@192.168.1.201:/share/Datas/Bad_Item/XM_Transmission/%s" % ("NEW_"+ str("%06d") % fld)
        # chan.send(sendCmd + "\n")
        # time.sleep(1)
        # chan.send("admin\n")
        # time.sleep(2)
        #
        # rtnStr = str(chan.recv(65535),encoding="UTF-8",errors="ignore")
        # print(rtnStr)
    except Exception as e:

        print(errinfo(),e)
        return False



if __name__ == "__main__":
    print()
    #
    # paramInfo = Get_Param_In_DB("QNAP_NAS")
    #
    # nasHost = paramInfo["NAS_HOST"]
    # nasPort = int(paramInfo["NAS_PORT"])
    # nasUser = paramInfo["NAS_USER"]
    # nasPasswd = paramInfo["NAS_PASSWD"]
    #
    # print(debug(),nasHost,nasPort,nasUser,nasPasswd)
    #
    # sshCmd = __Get_SSH_Hander(nasHost,nasPort,nasUser,nasPasswd)
    #
    # strCMD = "ls"
    # dd = __Linux_ExecCMD(sshCmd, strCMD)
    # print(dd)

    # rootUrl = paramInfo["KIC_ROOT_SITE"]







    rootDir = r"\\192.168.1.201\Datas\Bad_Item"
    for strRoot,lsDir,lsFiles in os.walk(rootDir):
        for strFile in lsFiles:

            singFullPathFileExt = os.path.join(strRoot,strFile)
            # print(debug(),__Get_File_MD5(singFullPathFileExt),strRoot,strFile)

            convRootPath = strRoot.replace(r"\\","\\\\")

            strSql = "select count(*) from nas_files where `all_path` = '%s' and `file_name` = '%s' and  `md5_string` = '%s' ;" % (convRootPath.replace("\\","\\\\"), strFile, __Get_File_MD5(singFullPathFileExt))
            # print(debug(),strSql)
            rtnCnt = mysqlExe.ExecQuery(strSql.encode('utf-8'))[0][0]
            if rtnCnt == 0:
                strSql = "select count(*) from nas_files where `md5_string` = '%s' ;" % (__Get_File_MD5(singFullPathFileExt))
                rtnCnt = mysqlExe.ExecQuery(strSql.encode('utf-8'))[0][0]
                if rtnCnt != 0:
                    flag = 1 # 已存在相同文件
                else:
                    flag = 0
                strSql = "INSERT INTO nas_files (`all_path`, `file_name`, `md5_string`, repeat_flag) VALUES ('%s', '%s', '%s', '%s');" % (convRootPath.replace("\\","\\\\"), strFile, __Get_File_MD5(singFullPathFileExt),flag)
                print(debug(),strSql)
                mysqlExe.ExecNonQuery(strSql.encode('utf-8'))
            else:
                print(debug(), r"跳过 %s" % (singFullPathFileExt))






