# -*- coding: utf-8 -*-
__author__ = 'SlovEnt'
__date__ = '2019/6/16 20:26'

import re
import os
import time
import random
import platform
from multiprocessing import Pool
from collections import OrderedDict
import traceback
from tpb_proc import tpb_proc_class
from tpb_proc import globParaList, mysqlConn
from ResPacks.get_url_html import chrome_get_html_all_content, get_html_all_content
from bs4 import BeautifulSoup

tpc = tpb_proc_class(mysqlConn,globParaList["TPB_ROOT_URL"])
tableName = "get_tpb_all_magnet"


def down_tpb_magent_info(singCategory):

    siteWeb = globParaList["TPB_ROOT_URL"]
    pageMaxNum = int(globParaList["TPB_DOWN_SUB_PAGE_MAX_NUM"]) + 1

    for i in range(0, pageMaxNum):

        enterHttpUrl = "{0}/browse/{1}/{2}/3".format(siteWeb, singCategory, i)
        subPostHtml = chrome_get_html_all_content(enterHttpUrl, "searchResult", "utf-8")
        soup = BeautifulSoup(subPostHtml, 'html.parser')

        nodes = soup.find_all(name="table", attrs={"id": "searchResult"})[0].find_all(name="tr")
        # nodes = soup.find_all(name="div", attrs={"class": "detName"})
        n = 0
        for node in nodes:
            '''
            `up_datetime` datetime DEFAULT NULL,
            `hash_string` varchar(128) NOT NULL,
            `up_user` varchar(255) DEFAULT NULL,
            `rs_name` varchar(1024) NOT NULL DEFAULT '',
            `rs_category` varchar(64) DEFAULT NULL,
            `rs_type` varchar(64) DEFAULT NULL,
            `up_size` varchar(12) DEFAULT NULL,
            `magnet` blob NOT NULL,
            `down_flag` char(1) DEFAULT '0',
            '''

            tpbDict = OrderedDict()

            if "detName" not in str(node):
                continue

            n += 1

            # print(node)
            tpbDict["rs_name"] = node.find_all(name="div")[0].a.text
            tpbDict["rs_name"] = tpbDict["rs_name"].replace("'", '"')
            tpbDict["rs_name"] = tpbDict["rs_name"].strip()

            tpbDict["magnet"] = node.find_all(name="td")[1].find_all(name="a")[1]["href"]

            tpbDict["hash_string"] = re.compile(r'''urn:btih:(.+?)&''').findall(tpbDict["magnet"])[0]

            # 加一个&结尾 便于后面正则表达式取值
            otherStr = "{0}&".format(node.find_all(name="td")[1].find_all(name="font")[0].text)
            otherStr = otherStr.replace("\xa0"," ")

            tpbDict["rs_category"] = node.find_all(name="td")[0].center.find_all(name="a")[0].text

            tpbDict["rs_type"] = node.find_all(name="td")[0].center.find_all(name="a")[1].text

            tpbDict["up_datetime"], tpbDict["up_size"], tpbDict["up_user"] = re.compile(r'''Uploaded (.+?), Size (.+?), ULed by (.+?)&''').findall(otherStr)[0]
            # print(tpbDict["up_datetime"])
            tpbDict["up_datetime"] = tpc.format_datetime(tpbDict["up_datetime"])

            tpbDict["down_flag"] = 0

            # print("99884", n, tpbDict)

            whereDict = OrderedDict()
            whereDict["hash_string"] = tpbDict["hash_string"]
            rtnData = tpc.table_row_is_exist(tableName, whereDict)

            # 通过触发器取下一个计数号
            totalNum = tpc.Get_SEQ_Next_Val("TPB_ALL_SEQ")

            if int(rtnData["CNT"]) != 0:
                print("11598 {2} : {0} {3} {4} {1} 已经存在".format(tpbDict["hash_string"], tpbDict["rs_name"], totalNum, tpbDict["rs_category"], tpbDict["rs_type"], ))
                continue

            rtnMsg = tpc.insert_row_table(tableName, tpbDict)

            if rtnMsg is True:
                print("11597 {2} : {0} {3} {4} {1} 已插入后台数据表".format(tpbDict["hash_string"], tpbDict["rs_name"], totalNum, tpbDict["rs_category"], tpbDict["rs_type"],))
            else:
                print("11596 {2} : {0} {3} {4} {1} 插入后台数据表失败".format(tpbDict["hash_string"], tpbDict["rs_name"], totalNum, tpbDict["rs_category"], tpbDict["rs_type"],))



def main():

    # 清空计数器 方便从0开始计数
    tpc.Set_SEQ_Init_Val("TPB_ALL_SEQ")

    allCategory = tpc.Get_DB_Dict("ALL")
    # allCategory = tpc.Get_DB_Dict("Porn")

    allCategory = random.sample(allCategory, len(allCategory))  # 随机打乱数组

    for singCategory in allCategory:

        down_tpb_magent_info(singCategory)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        traceback.print_exc()
