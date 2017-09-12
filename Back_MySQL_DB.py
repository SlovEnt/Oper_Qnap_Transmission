#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import time
import tarfile
import zipfile
from Comm_Func import *

'''''
mysqldump
Usage: mysqldump [OPTIONS] database [tables]
OR     mysqldump [OPTIONS] --databases [OPTIONS] DB1 [DB2 DB3...]
OR     mysqldump [OPTIONS] --all-databases [OPTIONS]
For more options, use mysqldump --help
'''

def zip_files(zip_src):
    f = zipfile.ZipFile(zip_dest, 'w', zipfile.ZIP_DEFLATED)
    f.write(zip_src)
    f.close()
    if os.path.exists(db_backup_name):
        os.remove(db_backup_name)

if __name__ == "__main__":

    dbInfo = Get_Param_Info("Config.ini")

    print(dbInfo)

    db_host = dbInfo["DB_HOST"]
    db_port = dbInfo["DB_PORT"]
    db_user = dbInfo["USER_NAME"]
    db_passwd = dbInfo["USER_PWD"]
    db_name = dbInfo["DB_NAME"]
    db_charset = "utf8"

    print("begin to dump mysql database %s ..." % db_host)
    db_backup_name = r"../mysql_dump/%s_v2PySql_%s.sql" % (db_host,time.strftime("%Y%m%d%H%M"))
    zip_src = db_backup_name
    zip_dest = zip_src + ".zip"
    str = r"D:\\UPUPW\\MariaDB\\bin\\mysqldump.exe -h%s -P%s -u%s -p%s %s --default_character-set=%s > %s" % (db_host, db_port, db_user, db_passwd, db_name, db_charset, db_backup_name)
    print(str)
    os.system(str)
    print("begin zip files...")
    zip_files(zip_src)
    print("done, pyhon is great!")

