# -*- coding: utf-8 -*-
__author__ = 'SlovEnt'
__date__ = '2018/5/6 15:42'


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


POST_ROOT_URL = "http://bbs169.com:8888"
ROOT_URL = "http://bbs169.com:8888/forum.php?mod=forumdisplay&fid=45"
ROOT_URL = "http://bbs169.com:8888/forum.php?mod=forumdisplay&fid=160"
DOWN_FLODERS = r"\\192.168.1.201\Datas\Bad_Item\Torrent_By_1024"

headers = { 'User-Agent' : "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36"}
headers = { 'Referer' : "http://bbs169.com:8888/forum.php?mod=forumdisplay&fid=45"}


if __name__ == "__main__":

    gmm = Get_1024_MagnetLink_Main(mysqlConn, ROOT_URL, DOWN_FLODERS, POST_ROOT_URL, headers)

    tableName = "craw_page_flag"

    for page in range(1, 20):

        subPageUrl = "{0}&page={1}".format(ROOT_URL, page)
        print("获取第{0}页帖子列表链接 {1}".format(page, subPageUrl))

        html = requests.get(url=subPageUrl, params=headers)
        html = html.content.decode('utf-8', 'ignore')

        # print(html)

        soup = BeautifulSoup(html, 'html.parser')

        forumNameDivContant = soup.find_all(name="div", attrs={"class": "z"})

        forumListName = forumNameDivContant[1].text
        forumListName = forumListName[-10:-1]
        forumListName = forumListName.replace("『 ","").replace(" ","")

        DOWN_FORUM_FLODERS = "{0}\{1}".format(DOWN_FLODERS, forumListName)

        isExists = os.path.exists(DOWN_FORUM_FLODERS)
        if not isExists:
            # 如果不存在则创建目录
            os.makedirs(DOWN_FORUM_FLODERS)

        forumNodes = soup.find_all(name="tbody", attrs={'id': re.compile("normalthread_.+?")})

        for forumNode in forumNodes:

            forumInfo = OrderedDict()

            forumInfo["web_name"] = "bbs169"
            forumInfo["id"] = forumNode.tr.th.a["id"]
            forumInfo["title"] = forumNode.tr.th.contents[8].string
            forumInfo["href"] = "{0}/{1}".format(POST_ROOT_URL, forumNode.tr.td.a["href"])
            forumInfo["search_flag"] = "0"

            whereDict = OrderedDict()
            whereDict["web_name"] = forumInfo["web_name"]
            whereDict["id"] = forumInfo["id"]

            rtnDatas = gmm.Table_Row_Is_Exist(tableName, whereDict)

            forumInfo["href"] = forumInfo["href"].replace("%", "%%")
            if rtnDatas["CNT"] == 0:
                rtnMsg = gmm.Inser_Init_TaskLog(tableName, forumInfo)

            forumInfo["href"] = forumInfo["href"].replace("%%", "%")

            whereDict["search_flag"] = "1"
            rtnDatas = gmm.Table_Row_Is_Exist(tableName, whereDict)

            if rtnDatas["CNT"] == 1 :
                ''' 已完成的 什么都不用做 '''
                pass

            else:

                print("帖子信息为", forumInfo)

                downSubFloder = forumInfo["title"].replace("\\", " ")
                downSubFloder = downSubFloder.replace("/", " ")
                downSubFloder = downSubFloder.replace("  ", " ")

                for x in range(0, len(downSubFloder)) :
                    # print(downSubFloder)
                    if downSubFloder[-1] == ".":
                        downSubFloder = downSubFloder[0:-1]

                for x in range(0, len(downSubFloder)) :
                    # print(downSubFloder)
                    if downSubFloder[-1] == " ":
                        downSubFloder = downSubFloder[0:-1]

                downSubFloder = "{0}\{1}".format(DOWN_FORUM_FLODERS, downSubFloder)

                print("下载目录设置", downSubFloder)

                # print(subFloder)

                isExists = os.path.exists(downSubFloder)
                if not isExists:
                    # 如果不存在则创建目录
                    os.makedirs(downSubFloder)

                subForumFileName = "{0}\{1}".format(downSubFloder, forumInfo["id"])

                htmlFileName = "{0}.html".format(subForumFileName)

                forumHtmlContant = gmm.Access_Url_RtnContent("get", htmlFileName, forumInfo["href"])

                # print(forumHtmlContant.decode('utf-8', 'ignore'))

                soup = BeautifulSoup(forumHtmlContant, 'html.parser')

                forumContant = soup.find_all(name="div", attrs={"class": "t_fsz"})
                forumContant = forumContant[0]
                # print(forumContant)

                imgLinkFlag = 0
                imgLists = forumContant.find_all(name="a", attrs={"href": re.compile("imageshack|imagetwist|imagexport")})



                if len(imgLists) == 0:
                    imgLinkFlag = 1
                    imgLists = forumContant.find_all(name="img", attrs={"src": re.compile("\.jpg|\.jpeg|\.png")})

                if len(imgLists) == 0:
                    imgLinkFlag = 2
                    imgLists = forumContant.find_all(name="img", attrs={"file": re.compile("\.jpg|\.jpeg|\.png")})

                n = 0
                for link in imgLists :

                    n += 1
                    filePrefix = '%03d' % n
                    if "imageshack" in  str(link) and imgLinkFlag == 0:
                        imgHtmlUrl = link["href"]
                        imgHtml = gmm.Access_Url_RtnContent("get", "", imgHtmlUrl)
                        soup = BeautifulSoup(imgHtml, 'html.parser')
                        imgsLink = soup.find_all(name="img", attrs={"id": "lp-image"})
                        imgsLink = imgsLink[0]["src"]
                        imgsLink = "{0}/{1}".format("https://imagizer.imageshack.com", imgsLink)

                    elif "imagexport" in str(link) and imgLinkFlag == 0:
                        imgHtmlUrl = link["href"]
                        imgHtml = gmm.Access_Url_RtnContent("get", "", imgHtmlUrl)
                        soup = BeautifulSoup(imgHtml, 'html.parser')
                        imgsLink = soup.find_all(name="img", attrs={"class": "pic img img-responsive"})
                        imgsLink = imgsLink[0]["src"]
                        # print(imgsLink)

                    elif imgLinkFlag == 1 :
                        imgsLink = link["src"]

                    elif imgLinkFlag == 2:
                        imgsLink = "{0}/{1}".format(POST_ROOT_URL, link["file"])

                    pass

                    # print(imgsLink)
                    # time.sleep(5)

                    fileName = os.path.basename(imgsLink)
                    imgFileName = "{0}_{1}".format(filePrefix, fileName)
                    print("开始下载图片 {0} to {1}\{2}".format(imgsLink, downSubFloder, imgFileName))
                    x = gmm.Access_Url_RtnContent("get", "{0}\{1}".format(downSubFloder, imgFileName), imgsLink)
                    # print(x)
                    # time.sleep(2)

                torrentLists = forumContant.find_all(name="a", attrs={'href': re.compile("forum.php\?mod=attachment&aid=.+?")})

                rtnMsg = False
                for link in torrentLists :

                    if ".torrent" in str(link) :
                        torrentLink = "{0}/{1}".format(POST_ROOT_URL, link["href"])
                        fileName = link.text
                        print("开始下载种子 {0} to {1}\{2}".format(torrentLink, downSubFloder, fileName))
                        rtnMsg = gmm.Access_Url_RtnContent("get", "{0}\{1}".format(downSubFloder, fileName), torrentLink)

                forumInfo["search_flag"] = "0"

                # print(rtnMsg)

                if rtnMsg != False :
                    forumInfo["search_flag"] = "1"

                whereDict = {}
                whereDict["web_name"] = forumInfo["web_name"]
                whereDict["id"] = forumInfo["id"]
                forumInfo["href"] = forumInfo["href"].replace("%", "%%")
                gmm.Update_Init_TaskLog(tableName, whereDict, forumInfo)

                print()

                # time.sleep(30)





