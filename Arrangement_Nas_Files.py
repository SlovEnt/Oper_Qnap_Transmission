import os
import time
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

def __Ssh_Login_Nas():
    sshTran = paramiko.Transport("xm.imchs.com", 22)
    sshTran.connect(username="root", password="Xm#Toor.1017")
    chan = sshTran.open_session()
    chan.settimeout(60)
    chan.get_pty()
    chan.invoke_shell()
    # sendCmd = "rsync -av --progress /userdisk/data/transmission/downloads/.  admin@192.168.1.201:/share/Datas/Bad_Item/XM_Transmission/%s" % ("NEW_"+ str("%06d") % fld)
    sendCmd = "rsync -av --progress /userdisk/data/transmission/downloads/.  admin@192.168.1.201:/share/Datas/Bad_Item/XM_Transmission/%s" % ("NEW_"+ str("%06d") % fld)
    chan.send(sendCmd + "\n")
    time.sleep(1)
    chan.send("admin\n")
    time.sleep(2)

    rtnStr = str(chan.recv(65535),encoding="UTF-8",errors="ignore")
    print(rtnStr)




if __name__ == "__main__":
    print()

    paramInfo = Get_Param_In_DB("NAS_CONN")

    print(paramInfo)

    nasHost = paramInfo[""]


    # rootUrl = paramInfo["KIC_ROOT_SITE"]







    # rootDir = r"\\192.168.1.201\Datas\Bad_Item"
    # for strRoot,lsDir,lsFiles in os.walk(rootDir):
    #     for strFile in lsFiles:
    #
    #         singFullPathFileExt = os.path.join(strRoot,strFile)
    #         # print(debug(),__Get_File_MD5(singFullPathFileExt),strRoot,strFile)
    #
    #         convRootPath = strRoot.replace(r"\\","\\\\")
    #
    #         strSql = "select count(*) from nas_files where `allpath` = '%s' and `file_name` = '%s' and  `md5_string` = '%s' ;" % (convRootPath, strFile, __Get_File_MD5(singFullPathFileExt))
    #         # print(debug(),strSql)
    #         rtnCnt = mysqlExe.ExecQuery(strSql.encode('utf-8'))[0][0]
    #         if rtnCnt == 0:
    #             strSql = "select count(*) from nas_files where `md5_string` = '%s' ;" % (__Get_File_MD5(singFullPathFileExt))
    #             rtnCnt = mysqlExe.ExecQuery(strSql.encode('utf-8'))[0][0]
    #             if rtnCnt != 0:
    #                 flag = 1 # 已存在相同文件
    #             else:
    #                 flag = 0
    #             strSql = "INSERT INTO nas_files (`allpath`, `file_name`, `md5_string`, flag) VALUES ('%s', '%s', '%s', '%s');" % (convRootPath.replace("\\","\\\\"), strFile, __Get_File_MD5(singFullPathFileExt),flag)
    #             print(debug(),strSql)
    #             mysqlExe.ExecNonQuery(strSql.encode('utf-8'))
    #         else:
    #             print(debug(), r"跳过 %s" % (singFullPathFileExt))







