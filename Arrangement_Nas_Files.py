import os
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





if __name__ == "__main__":
    print()
    rootDir = r"\\192.168.1.201\Datas\Bad_Item"
    for strRoot,lsDir,lsFiles in os.walk(rootDir):
        for strFile in lsFiles:

            singFullPathFileExt = os.path.join(strRoot,strFile)
            # print(debug(),__Get_File_MD5(singFullPathFileExt),strRoot,strFile)

            convRootPath = strRoot.replace(r"\\","\\\\")

            strSql = "select count(*) from nas_files where `allpath` = '%s' and `file_name` = '%s' and  `md5_string` = '%s' ;" % (convRootPath, strFile, __Get_File_MD5(singFullPathFileExt))
            # print(debug(),strSql)
            rtnCnt = mysqlExe.ExecQuery(strSql.encode('utf-8'))[0][0]
            if rtnCnt == 0:
                strSql = "select count(*) from nas_files where `md5_string` = '%s' ;" % (__Get_File_MD5(singFullPathFileExt))
                rtnCnt = mysqlExe.ExecQuery(strSql.encode('utf-8'))[0][0]
                if rtnCnt != 0:
                    flag = 1 # 已存在相同文件
                else:
                    flag = 0
                strSql = "INSERT INTO nas_files (`allpath`, `file_name`, `md5_string`, flag) VALUES ('%s', '%s', '%s', '%s');" % (convRootPath.replace("\\","\\\\"), strFile, __Get_File_MD5(singFullPathFileExt),flag)
                print(debug(),strSql)
                mysqlExe.ExecNonQuery(strSql.encode('utf-8'))
            else:
                print(debug(), r"跳过 %s" % (singFullPathFileExt))







