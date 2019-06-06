# -*- coding: utf-8 -*-
__author__ = 'SlovEnt'
__date__ = '2019/5/11 9:26'

import time
import os
import re
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict

novelId = "55_55029" # 长相思(全集）
ROOT_URL = "https://www.23wx.so/{0}/".format(novelId)
DOWN_FLODERS = r"E:\下载小说"

headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}
headers = { 'Host' : ROOT_URL}
headers = { 'Referer' : ROOT_URL}
headers = { 'Upgrade-Insecure-Requests' : '1'}


def rtn_chapter_list_info(html):

    soup = BeautifulSoup(html, 'html.parser')
    novelName = soup.find_all(name="div", attrs={"id": "info"})[0].h1.text
    # print(novelName)

    chapterListInfoSoup = soup.find_all(name="dd")

    chapterListInfoArr = []

    for ddItem in chapterListInfoSoup:

        chapterListInfoDict = OrderedDict()

        if "href" not in str(ddItem):
            continue

        chapterListInfoDict["text"] = ddItem.a.text
        chapterListInfoDict["href"] = ddItem.a["href"]
        # print(chapterListInfoDict)

        chapterListInfoArr.append(chapterListInfoDict)

    return chapterListInfoArr, novelName

def rtn_chapter_txt(chapterHtml):

    soup = BeautifulSoup(chapterHtml, 'html.parser')

    txtContent = soup.find_all(name="div", attrs={"id": "content"})[0].text

    txtContent = txtContent.replace("一秒记住【顶点小说网 www.23wx.so】，精彩小说无弹窗免费阅读！", "")
    txtContent = txtContent.replace("       ", "")
    txtContent = txtContent.replace("        ", "")
    txtContent = txtContent.replace("    ", "")
    txtContent = txtContent.replace(" ", "")
    txtContent = txtContent.replace("～", "")
    txtContent = txtContent.replace("\r\n", "")
    txtContent = txtContent.replace("\n\n", "")

    return txtContent

def write_txt_content(txtFileName, chapterName, chapterTxt):
    with open(txtFileName, 'a') as f:
        f.write(chapterName + "\n")
        f.write(chapterTxt + "\n\n")

def get_html_all_content(url):
    getFlag = False
    while getFlag == False:
        try:
            html = requests.get(url=url, params=headers)
            html = html.content.decode('gbk', 'ignore')
            getFlag = True
        except Exception as e:
            print(url, e)
            getFlag = False
            time.sleep(5)
    return html

if __name__ == '__main__':

    html = get_html_all_content(ROOT_URL)

    # 返回章节信息
    chapterListInfo, novelName = rtn_chapter_list_info(html)

    novelFilePath = r"{0}\{1}.txt".format(DOWN_FLODERS, novelName)

    if os.path.exists(novelFilePath):
        os.remove(novelFilePath)

    for chapterInfo in chapterListInfo:
        # print(chapterInfo)

        chapterUrl = "{0}/{1}".format(ROOT_URL, chapterInfo["href"])

        chapterHtml = get_html_all_content(chapterUrl)

        chapterTxt = rtn_chapter_txt(chapterHtml)

        print(novelFilePath, chapterInfo["text"])
        write_txt_content(novelFilePath, chapterInfo["text"], chapterTxt)

