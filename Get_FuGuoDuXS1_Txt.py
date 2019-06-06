# -*- coding: utf-8 -*-
__author__ = 'SlovEnt'
__date__ = '2019/5/4 20:08'


import time
import os
import re
import requests
from bs4 import BeautifulSoup


# 单一小说网址
# NOVEL_URL = 'http://www.dzwx.org/7_7435/'
NOVEL_URL = 'https://www.fuguoduxs.com/7_7186/'
# NOVEL_URL = 'https://www.fuguodu1.com/7_7186/'

CHAPTER_POST = 1

headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}
headers = { 'Host' : '9453hot.com'}
headers = { 'Referer' : 'https://www.fuguoduxs.com/'}
headers = { 'Upgrade-Insecure-Requests' : '1'}
# headers = { 'Cookie' : '{0}'.format("djsk_2132_saltkey=W5zSRrzA; djsk_2132_lastvisit=1525257765; UM_distinctid=16320aa25276de-054e64fd4be03b-3f63440c-140000-16320aa252880e; djsk_2132_visitedfid=46D58; visid_incap_840311=1IRaRsdLRX6s8/Svt4FqZzSk6VoAAAAAQUIPAAAAAACLbrjvf/mhLSbIbAbMRXtJ; incap_ses_432_840311=R/UWSsCf0TF07B+95Mb+Bfyv6VoAAAAABZ+7li8gWgY8liDu9KuxEw==; djsk_2132_st_t=0%7C1525266655%7C6ee60796e3f603e08ce5f538e4e897d2; djsk_2132_forum_lastvisit=D_58_1525261404D_46_1525266655; djsk_2132_st_p=0%7C1525267310%7Ccea5be0db24a3396de6751b700dade9d; djsk_2132_viewid=tid_236869; djsk_2132_sendmail=1; CNZZDATA1257937871=166026316-1525256282-http%253A%252F%252F9453hot.com%252F%7C1525267082; __tins__19465647=%7B%22sid%22%3A%201525266427309%2C%20%22vd%22%3A%2018%2C%20%22expires%22%3A%201525269111175%7D; __51cke__=; __51laig__=28; djsk_2132_sid=UndopY; djsk_2132_lastact=1525267373%09forum.php%09ajax")}


html = requests.get(url=NOVEL_URL, params=headers)
html = html.content.decode('gbk', 'ignore')
# print(html)

soup = BeautifulSoup(html, 'html.parser')

txtFileName = soup.find_all(name="div", attrs={"id": "info"})[0].h1.text

allTxtFileName = "{0}.txt".format(txtFileName)
allTxtFileName = allTxtFileName.replace("/", "、")
allTxtFileNamePath = r"\\SE-NAS\Public\Temp\{0}".format(allTxtFileName)

if CHAPTER_POST == 1:
    if (os.path.exists(allTxtFileNamePath)):
        os.remove(allTxtFileNamePath)

print("文件下载路径：{0}".format(allTxtFileNamePath))

chapterList = soup.find_all(name="dd")
n=0
for chapterInfo in chapterList:

    # time.sleep(2)

    n += 1
    print(n, chapterInfo)

    if n < CHAPTER_POST:
        continue

    chapterName = "{0} - {1}".format('%03d' % n, chapterInfo.find_all(name="a")[0].text)
    chapterUrl = "{0}{1}".format("https://www.fuguoduxs.com", chapterInfo.find_all(name="a")[0]['href'])
    print(chapterName, chapterUrl)

    chapterHtml = requests.get(url=chapterUrl, params=headers)
    chapterHtml = chapterHtml.content.decode('gbk', 'ignore')
    # print(chapterHtml)

    chapterSoup = BeautifulSoup(chapterHtml, 'html.parser')

    textOne = chapterSoup.find_all(name="div", attrs={"id": "content"})[0].text
    # textOne = chapterSoup.find_all(name="div", attrs={"id": "list"})[0].text
    textOne = textOne.replace("\n\r", "\n")
    textOne = textOne.replace("    ", "")



    textTwo = ""

    print(textOne)

    with open(allTxtFileNamePath, 'a', encoding='utf-8') as f:

        f.write("\n\n")
        # f.write("{0}\n\n".format(chapterName))
        f.write(textOne)










