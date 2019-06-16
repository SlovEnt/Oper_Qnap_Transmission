# -*- coding: utf-8 -*-
__author__ = 'SlovEnt'
__date__ = '2019/6/16 20:26'

import re
import os
import time
import random
import platform
from multiprocessing import Pool
import traceback
from tpb_proc import tpb_proc_class
from tpb_proc import globParaList, mysqlConn
from ResPacks.get_url_html import chrome_get_html_all_content, get_html_all_content
from bs4 import BeautifulSoup

tpc = tpb_proc_class(mysqlConn,globParaList["TPB_ROOT_URL"])

def down_tpb_magent_info(singCategory):

    siteWeb = globParaList["TPB_ROOT_URL"]
    pageMaxNum = int(globParaList["TPB_DOWN_SUB_PAGE_MAX_NUM"]) + 1

    for i in range(0, pageMaxNum):

        enterHttpUrl = "{0}/browse/{1}/{2}/3".format(siteWeb, singCategory, i)
        subPostHtml = get_html_all_content(enterHttpUrl, "searchResult", "utf-8")
        soup = BeautifulSoup(subPostHtml, 'html.parser')

        nodes = soup.find_all(name="table", attrs={"id": "searchResult"})[0].find_all(name="tr")

        for node in nodes:
            print(node)






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
