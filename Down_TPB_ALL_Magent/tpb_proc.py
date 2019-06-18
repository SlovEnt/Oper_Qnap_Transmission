# -*- coding: utf-8 -*-
__author__ = 'SlovEnt'
__date__ = '2019/6/16 20:31'

import os
from selenium import webdriver
from ResPacks.UsedCommFuncs import Get_Param_Info
from ResPacks import torndb
import datetime
import re
from collections import OrderedDict
import traceback

# 参数加载区
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG_FILE = "{0}/Config.ini".format(BASE_DIR)
globParaList = Get_Param_Info(CONFIG_FILE)

# 引入mysql操作函数
mysqlConn = torndb.Connection(
    "{0}:{1}".format(globParaList["DB_HOST"],globParaList["DB_PORT"]),
    globParaList["DB_NAME"],
    globParaList["USER_NAME"],
    globParaList["USER_PWD"],
)



class tpb_proc_class(object):

    def __init__(self, mysqlConn, ROOT_URL):
        self.mysqlConn = mysqlConn
        self.ROOT_URL = ROOT_URL

    def Set_SEQ_Init_Val(self, seq_name):
        setSeqInitVal = "select setval('" + seq_name + "',0);"
        self.mysqlConn.execute(setSeqInitVal.encode('utf-8'))

    def Get_SEQ_Next_Val(self, seq_name):
        getSeqNextVal = "select nextval('" + seq_name + "');"
        listsql = self.mysqlConn.execute(getSeqNextVal.encode('utf-8'))
        seqVal = int(listsql)
        return seqVal

    def Get_DB_Dict(self, rs_group):
        if rs_group == "ALL":
            sqlStr = "select dict_id from sys_dict where dict_the = 'tpb';"
        else:
            sqlStr = "select dict_id from sys_dict where dict_the = 'tpb' and dict_item = '" + rs_group + "';"
        listDatas = self.mysqlConn.query(sqlStr.encode('utf-8'))
        groupList = []
        for singData in listDatas:
            groupList.append(singData["dict_id"])
        return groupList

    def format_datetime(self, up_datetime):
        # 11-22&nbsp;2016
        # 02-06&nbsp;18:05
        # Y-day&nbsp;23:36
        # Today&nbsp;02:02
        # <b>7&nbsp;mins&nbsp;ago</b>
        # 10-17&nbsp;2008
        if 'Y-day' in up_datetime:
            today = datetime.date.today()
            oneday = datetime.timedelta(days=1)
            yesterday = today - oneday
            up_datetime = yesterday.strftime('%Y-%m-%d') + " " + up_datetime[-5:]+":00"
        elif 'ago' in up_datetime:
            today = datetime.datetime.now()
            oneday = datetime.timedelta(hours=8)
            yesterday = today - oneday
            mins = re.sub("\D", "",up_datetime[0:9])
            oneday = datetime.timedelta(minutes=int(mins))
            yesterday = yesterday-oneday
            up_datetime = yesterday.strftime('%Y-%m-%d %H:%M:%S')
        elif 'Today' in up_datetime:
            up_datetime = datetime.datetime.now().strftime('%Y-%m-%d') + " " + up_datetime[-5:]+":00"
        elif ' 201' in up_datetime:
            up_datetime = up_datetime[-4:] + "-" + up_datetime[0:2] + "-" + up_datetime[3:5] + " " + "00:00:00"
        elif ' 202' in up_datetime:
            up_datetime = up_datetime[-4:] + "-" + up_datetime[0:2] + "-" + up_datetime[3:5] + " " + "00:00:00"
        elif ' 200' in up_datetime:
            up_datetime = up_datetime[-4:] + "-" + up_datetime[0:2] + "-" + up_datetime[3:5] + " " + "00:00:00"
        else:
            up_datetime = datetime.datetime.now().strftime('%Y') + "-" + up_datetime[0:2] + "-" + up_datetime[3:5] + " " + up_datetime[-5:]+":00"
        return up_datetime

    def table_row_is_exist(self, tableName, whereDict):
        ''' 返回指定条件下返回的ROW数据总数 '''
        strSql = "SELECT * FROM {0} WHERE 0=0".format(tableName)
        strWhere = ""
        for key, value in whereDict.items():
            strWhere = strWhere + " " + "AND {0}='{1}'".format(key, value)

        strSql = strSql + strWhere

        rtnDatas = OrderedDict()

        # print(strSql)
        rtnDBDatas = self.mysqlConn.query(strSql)

        rtnDatas["CNT"] = len(rtnDBDatas)
        rtnDatas["CONTENT"] = rtnDBDatas
        # rtnDatas["STRWHERE"] = strWhere.replace(strWhere[0:4], "")
        rtnDatas["STRSQL"] = strSql

        return rtnDatas

    def insert_row_table(self, tableName, tpbDict):
        fieldList = ""
        valueList = ""
        for key, value in tpbDict.items():
            if fieldList == "":
                fieldList = "{0}".format(key)
                valueList = "'{0}'".format(value)
            else:
                fieldList = "{0}, {1}".format(fieldList, key)
                valueList = "{0}, '{1}'".format(valueList, value)
        strSql = "INSERT INTO {0} ({1}) VALUES ({2});".format(tableName, fieldList, valueList)
        # print(strSql)
        try:
            self.mysqlConn.execute(strSql)
            return True
        except Exception as e:
            print(strSql)
            traceback.print_exc()
            print(e)
            return e
