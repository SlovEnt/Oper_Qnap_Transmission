# -*- coding: utf-8 -*-
__author__ = 'SlovEnt'
__date__ = '2018/5/2 20:47'

import time
import os
import re
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
from ResPacks import torndb
from ResPacks.UsedCommFuncs import Get_Param_Info
from Get_1024_MagnetLink_Proc import Get_1024_MagnetLink_Main


ROOT_URL = """https://hitomi.la/galleries/1276212.html"""
mb = "aa"
DOWN_FLODERS = r"\\192.168.31.201\Datas\Bad_Item\kb9453"

headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}
headers = { 'Host' : '9453hot.com'}
headers = { 'Referer' : 'http://www.9453hot.com/forum-46-1.html'}
headers = { 'Upgrade-Insecure-Requests' : '1'}
# headers = { 'Cookie' : '{0}'.format("djsk_2132_saltkey=W5zSRrzA; djsk_2132_lastvisit=1525257765; UM_distinctid=16320aa25276de-054e64fd4be03b-3f63440c-140000-16320aa252880e; djsk_2132_visitedfid=46D58; visid_incap_840311=1IRaRsdLRX6s8/Svt4FqZzSk6VoAAAAAQUIPAAAAAACLbrjvf/mhLSbIbAbMRXtJ; incap_ses_432_840311=R/UWSsCf0TF07B+95Mb+Bfyv6VoAAAAABZ+7li8gWgY8liDu9KuxEw==; djsk_2132_st_t=0%7C1525266655%7C6ee60796e3f603e08ce5f538e4e897d2; djsk_2132_forum_lastvisit=D_58_1525261404D_46_1525266655; djsk_2132_st_p=0%7C1525267310%7Ccea5be0db24a3396de6751b700dade9d; djsk_2132_viewid=tid_236869; djsk_2132_sendmail=1; CNZZDATA1257937871=166026316-1525256282-http%253A%252F%252F9453hot.com%252F%7C1525267082; __tins__19465647=%7B%22sid%22%3A%201525266427309%2C%20%22vd%22%3A%2018%2C%20%22expires%22%3A%201525269111175%7D; __51cke__=; __51laig__=28; djsk_2132_sid=UndopY; djsk_2132_lastact=1525267373%09forum.php%09ajax")}


html = requests.get(url=ROOT_URL, params=headers)
html = html.content.decode('utf-8', 'ignore')
print(html)
#
soup = BeautifulSoup(html, 'html.parser')

floderName = soup.find_all(name="div", attrs={"class": "gallery"})[0].h1.a.text
floderName = floderName.replace("<","(").replace(">",")").replace(" ","").replace("|","")

print("--------------------------------------")
print(floderName)

downSubFloder = "{0}\{1}".format(DOWN_FLODERS, floderName)
isExists = os.path.exists(downSubFloder)
if not isExists:
    # 如果不存在则创建目录
    os.makedirs(downSubFloder)

# 从节点中获取所有图片资源链接
imgList = soup.find_all(name="script")
dataReg = re.compile(r"'(.+?).jpg'")
rawDatas = dataReg.findall(str(imgList))
# print(rawDatas)


for img in rawDatas :
    imgLink = "https:{0}".format(img)
    imgLink = imgLink.replace("tn.hitomi.la","{0}.hitomi.la".format(mb)).replace("smalltn","galleries")
    # print(imgLink)
    filename = os.path.basename(imgLink)
    testname = "{0}\{1}".format(downSubFloder, filename)
    while True :
        try :
            print("已下载", imgLink)
            response = requests.get(url=imgLink, params=headers)
            with open(testname, "wb") as code:
                code.write(response.content)
            break

        except Exception as e:
            print(e)

