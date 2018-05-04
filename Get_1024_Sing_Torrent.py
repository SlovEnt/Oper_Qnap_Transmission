# -*- coding: utf-8 -*-
__author__ = 'SlovEnt'
__date__ = '2018/5/3 19:00'


import time
import os
import re
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
from ResPacks import torndb
from ResPacks.UsedCommFuncs import Get_Param_Info
from Get_1024_MagnetLink_Proc import Get_1024_MagnetLink_Main
from multiprocessing import Pool

import sys
sys.setrecursionlimit(1000000)

globParaList = Get_Param_Info("./Config.ini")

# 引入mysql操作函数
mysqlConn = torndb.Connection(
    "{0}:{1}".format(globParaList["DB_HOST"],globParaList["DB_PORT"]),
    globParaList["DB_NAME"],
    globParaList["USER_NAME"],
    globParaList["USER_PWD"],
)


ROOT_URL = "http://w2.aqu1024.net/pw/thread.php?fid=5"
ROOT_URL = "http://w2.aqu1024.net/pw/thread.php?fid=22"

DOWN_FLODERS = r"\\192.168.1.201\Datas\Bad_Item\Torrent_By_1024\00.YZWM"
DOWN_FLODERS = r"\\192.168.1.201\Datas\Bad_Item\Torrent_By_1024\00.RBQB"

POST_ROOT_URL = "http://w2.aqu1024.net/pw"

headers = { 'User-Agent' : " 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'" }
# headers = { 'Referer' : "http://www3.uptorrentfilespacedownhostabc.com/updowm/file.php/P7FU2Xp.html" }
# headers = { 'Referer' : "http://www1.downsx.com/torrent/D1A1C877CC6D4636A3A3C42D8E52DA0F9DF73F48" }

tableName = "craw_page_flag"
gmm = Get_1024_MagnetLink_Main(mysqlConn, ROOT_URL, DOWN_FLODERS, POST_ROOT_URL, headers)


def Down_1024SingTorrent(node):

    if "置顶帖标志" not in str(node):

        postNode = OrderedDict()

        postNode["web_name"] = "1024_YZWM"
        postNode["id"] = node["id"]
        postNode["title"] = node.h3.text.replace("?", "").replace("\\",".").replace("/",".")
        postNode["href"] = "{0}/{1}".format(POST_ROOT_URL, node.h3.a["href"])
        postNode["search_flag"] = "0"

        whereDict = OrderedDict()
        whereDict["web_name"] = postNode["web_name"]
        whereDict["id"] = postNode["id"]

        rtnDatas = gmm.Table_Row_Is_Exist(tableName, whereDict)

        if rtnDatas["CNT"] == 0:
            rtnMsg = gmm.Inser_Init_TaskLog(tableName, postNode)

        whereDict["search_flag"] = "1"
        rtnDatas = gmm.Table_Row_Is_Exist(tableName, whereDict)

        if rtnDatas["CNT"] == 1:
            ''' 已完成的 什么都不用做 '''
            pass

        else:

            print("帖子标题为", postNode["id"], postNode["title"])

            downSubFloder = "{0}\{2}_{1}".format(DOWN_FLODERS, postNode["title"], postNode["id"])
            isExists = os.path.exists(downSubFloder)
            if not isExists:
                # 如果不存在则创建目录
                os.makedirs(downSubFloder)

            fileName = "{0}\{1}".format(downSubFloder, "0000.html")
            contentText = gmm.Access_Url_RtnContent("get", fileName, postNode["href"], data={})
            html = contentText.decode('utf-8', 'ignore')
            # print(html)
            soup = BeautifulSoup(html, 'html.parser')
            divNodes = soup.find_all(name="div", attrs={"id": "read_tpc"})
            print(divNodes)

            for node in divNodes:
                # 从节点中获取所有图片资源链接
                imgPre = re.compile(r"""src="(.+?)"/>""")
                imgLinks = gmm.Is_Re_Correctly(str(node), imgPre, "图片链接")

                for imgUrl in imgLinks:
                    print("获取图片链接", imgUrl)
                    fileName = os.path.basename(imgUrl)
                    fileName = fileName.replace("*","")
                    fileName = "{0}\{1}".format(downSubFloder, fileName)
                    gmm.Access_Url_RtnContent("get", fileName, imgUrl, data={})

                torrentPre = re.compile(r"""<a href="(.+?)" target="_blank">.+?</a>""")
                torrentLinks = gmm.Is_Re_Correctly(str(node), torrentPre, "种子链接")

                rtnMsg = 0
                for torrentUrl in torrentLinks:

                    torrentUrl = torrentUrl.replace("&lt;br&gt;&lt;br&gt","")

                    fileName = "{0}\{1}.torrent".format(downSubFloder, postNode["id"])

                    if "downsx" in torrentUrl:
                        print("剥离下载链接：", torrentUrl)
                        response = gmm.Access_Url_RtnContent("get", "", torrentUrl, data={})
                        soup = BeautifulSoup(response, 'html.parser')
                        divNodes = soup.find_all(name="div", attrs={"class": "uk-width-1-1 uk-text-center dlboxbg"})
                        preTorrentDownUrl = divNodes[0].find_all("a")[1]["href"]
                        # print(divNodes)
                        torrentArr = torrentUrl.split("/torrent")
                        newDownLink = "{0}{1}".format(torrentArr[0], preTorrentDownUrl)

                        print("实际下载链接：", newDownLink)
                        rtnMsg = gmm.Access_Url_RtnContent("post", fileName, newDownLink, downUrl=torrentUrl, data={})

                    elif "uptorrentfilespacedownhostabc" in torrentUrl:
                        print("剥离下载链接：", torrentUrl)
                        response = gmm.Access_Url_RtnContent("get", "", torrentUrl, data={})
                        print(response)

                    elif "qqxbt" in torrentUrl:
                        print("剥离下载链接：", torrentUrl)
                        newDownLink = torrentUrl.replace("Public", "Download")
                        print("实际下载链接：", newDownLink)
                        rtnMsg = gmm.Access_Url_RtnContent("post", fileName, newDownLink, downUrl=torrentUrl, data={})

            if rtnMsg != 0:

                postNode["search_flag"] = "1"

                whereDict = {}
                whereDict["web_name"] = postNode["web_name"]
                whereDict["id"] = postNode["id"]

                gmm.Update_Init_TaskLog(tableName, whereDict, postNode)

            else:

                postNode["search_flag"] = "2"

                whereDict = {}
                whereDict["web_name"] = postNode["web_name"]
                whereDict["id"] = postNode["id"]

                gmm.Update_Init_TaskLog(tableName, whereDict, postNode)


if __name__ == "__main__":

    try :

        for pageNum in range(1, 100):

            subPageUrl = "{0}&page={1}".format(ROOT_URL, pageNum)

            html = requests.get(url=subPageUrl, params=headers)
            html = html.content.decode('utf-8', 'ignore')
            soup = BeautifulSoup(html, 'html.parser')
            divNodes = soup.find_all(name="td", attrs={"style": "text-align:left;padding-left:8px"})

            p = Pool(5)
            for node in divNodes:
                p.apply_async(Down_1024SingTorrent, args=(node,))
            p.close()
            p.join()

    except Exception as e:
        print(e)
