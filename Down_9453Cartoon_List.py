# -*- coding: utf-8 -*-
__author__ = 'SlovEnt'
__date__ = '2018/5/2 22:55'

import time
import os
import re
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
from ResPacks import torndb
from ResPacks.UsedCommFuncs import Get_Param_Info
from Get_1024_MagnetLink_Proc import Get_1024_MagnetLink_Main

globParaList = Get_Param_Info("./Config.ini")

# 引入mysql操作函数
mysqlConn = torndb.Connection(
    "{0}:{1}".format(globParaList["DB_HOST"],globParaList["DB_PORT"]),
    globParaList["DB_NAME"],
    globParaList["USER_NAME"],
    globParaList["USER_PWD"],
)

ROOT_URL = "http://www.kb986.com"
# ROOT_URL = "http://www.kb986.com/thread-236868-1-1.html"

DOWN_FLODERS = r"\\192.168.1.201\Datas\Bad_Item\kb9453"

headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}
headers = { 'Host' : 'www.kb986.com'}
headers = { 'Referer' : 'http://www.kb986.com/forum-46-1.html'}
headers = { 'Upgrade-Insecure-Requests' : '1'}
# headers = { 'Cookie' : '{0}'.format("djsk_2132_saltkey=W5zSRrzA; djsk_2132_lastvisit=1525257765; UM_distinctid=16320aa25276de-054e64fd4be03b-3f63440c-140000-16320aa252880e; djsk_2132_visitedfid=46D58; visid_incap_840311=1IRaRsdLRX6s8/Svt4FqZzSk6VoAAAAAQUIPAAAAAACLbrjvf/mhLSbIbAbMRXtJ; incap_ses_432_840311=R/UWSsCf0TF07B+95Mb+Bfyv6VoAAAAABZ+7li8gWgY8liDu9KuxEw==; djsk_2132_st_t=0%7C1525266655%7C6ee60796e3f603e08ce5f538e4e897d2; djsk_2132_forum_lastvisit=D_58_1525261404D_46_1525266655; djsk_2132_st_p=0%7C1525267310%7Ccea5be0db24a3396de6751b700dade9d; djsk_2132_viewid=tid_236869; djsk_2132_sendmail=1; CNZZDATA1257937871=166026316-1525256282-http%253A%252F%252F9453hot.com%252F%7C1525267082; __tins__19465647=%7B%22sid%22%3A%201525266427309%2C%20%22vd%22%3A%2018%2C%20%22expires%22%3A%201525269111175%7D; __51cke__=; __51laig__=28; djsk_2132_sid=UndopY; djsk_2132_lastact=1525267373%09forum.php%09ajax")}


if __name__ == "__main__":

    tableName = "craw_page_flag"

    for page in range(1, 137):

        subPageUrl = "{0}/forum-46-{1}.html".format(ROOT_URL, page)

        print(subPageUrl)

        html = requests.get(url=ROOT_URL, params=headers, timeout=30)

        pageFileName = r"{0}\0000.html".format(r"\\192.168.1.201\Datas\Bad_Item\kb9453")


        with open(pageFileName, "wb") as code:
            code.write(html.content)

        html = html.content.decode('utf-8', 'ignore')

        soup = BeautifulSoup(html, 'html.parser')
        tableContant = soup.find_all(name="span", attrs={"class": "comiis_common"})

        print(tableContant)

        for x in tableContant:
            print(x)




