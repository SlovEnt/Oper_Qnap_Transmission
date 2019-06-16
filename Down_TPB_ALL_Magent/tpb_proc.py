# -*- coding: utf-8 -*-
__author__ = 'SlovEnt'
__date__ = '2019/6/16 20:31'

import os
from selenium import webdriver
from ResPacks.UsedCommFuncs import Get_Param_Info
from ResPacks import torndb

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

