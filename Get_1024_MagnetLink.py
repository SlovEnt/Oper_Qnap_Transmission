# -*- coding: utf-8 -*-
__author__ = 'SlovEnt'
__date__ = '2018/4/29 16:59'


import time
import os
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


ROOT_URL = "http://1024.917rbb.info/pw/thread.php?fid=3"

DOWN_FLODERS = r"\\192.168.1.201\Datas\Bad_Item\Torrent_By_1024\00.Collection"

POST_ROOT_URL = "http://w2.aqu1024.net/pw"

headers = { 'User-Agent' : " 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'" }
# headers = { 'Referer' : "http://www3.uptorrentfilespacedownhostabc.com/updowm/file.php/P7FU2Xp.html" }
# headers = { 'Referer' : "http://www1.downsx.com/torrent/D1A1C877CC6D4636A3A3C42D8E52DA0F9DF73F48" }
# #
# #
# #
# url = "http://www1.downsx.com/Download/25037db91ce21c4f"
# # data = {'type':'torrent','id':'P7FU2Xp','name':'xp1024.com_207-5.zip'}
# #
# response = requests.post(url, headers = headers)
# # print(torrfile.content)
# testname = "sdfds.zip.torrent"
# with open(testname, "wb") as code:
#     code.write(response.content)

# req = request.Request(url=ROOT_URL, headers=HEADERS)
# pageSourceScript = request.urlopen(req).read().decode('utf-8', 'ignore')

# print("sdfsd")
# time.sleep(600)

if __name__ == "__main__":

    gmm = Get_1024_MagnetLink_Main(mysqlConn, ROOT_URL, DOWN_FLODERS, POST_ROOT_URL, headers)

    tableName = "craw_page_flag"
    # gmm.Get_All_Post_Url(tableName)

    for page in range(1, 30):

        subPageUrl = "{0}&page={1}".format(ROOT_URL, page)

        html = requests.get(url=subPageUrl, params=headers)
        html = html.content.decode('utf-8', 'ignore')
        soup = BeautifulSoup(html, 'html.parser')

        nodes = soup.find_all(name="tr", attrs={"class": "tr3 t_one", "align": "center"})

        for node in nodes:
            postNode = OrderedDict()

            if "置顶帖标志" not in str(node):
                # print(type(node), node.a)
                postNode["web_name"] = "1024"
                postNode["id"] = node.h3.a["id"]
                postNode["title"] = node.h3.a.text.replace("\xa0", "")
                postNode["href"] = "{0}/{1}".format(POST_ROOT_URL, node.h3.a["href"])
                postNode["search_flag"] = "0"

                whereDict = OrderedDict()
                whereDict["web_name"] = postNode["web_name"]
                whereDict["id"] = postNode["id"]

                rtnDatas = gmm.Table_Row_Is_Exist(tableName, whereDict)

                if rtnDatas["CNT"] == 0 :
                    rtnMsg = gmm.Inser_Init_TaskLog(tableName, postNode)

                whereDict["search_flag"] = "1"
                rtnDatas = gmm.Table_Row_Is_Exist(tableName, whereDict)

                if rtnDatas["CNT"] == 1 :
                    ''' 已完成的 什么都不用做 '''
                    pass

                else:

                    print("帖子标题为", postNode["id"], postNode["title"])

                    downSubFloder = "{0}\{2}_{1}".format(DOWN_FLODERS, postNode["title"], postNode["id"])
                    isExists = os.path.exists(downSubFloder)
                    if not isExists:
                        # 如果不存在则创建目录
                        os.makedirs(downSubFloder)

                    rtnMsg = gmm.Get_Post_Content_List(tableName, postNode, downSubFloder)

                    if rtnMsg != 0 :

                        postNode["search_flag"] = "1"

                        whereDict = {}
                        whereDict["web_name"] = postNode["web_name"]
                        whereDict["id"] = postNode["id"]

                        gmm.Update_Init_TaskLog(tableName, whereDict, postNode)

                    else :

                        postNode["search_flag"] = "2"

                        whereDict = {}
                        whereDict["web_name"] = postNode["web_name"]
                        whereDict["id"] = postNode["id"]

                        gmm.Update_Init_TaskLog(tableName, whereDict, postNode)

                        print()
                        print()
                        print()
