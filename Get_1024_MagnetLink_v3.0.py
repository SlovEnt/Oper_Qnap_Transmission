# -*- coding: utf-8 -*-
__author__ = 'SlovEnt'
__date__ = '2018/4/29 16:59'


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


ROOT_URL = "http://s2.91sgc.rocks/pw/thread.php?fid=3"
ROOT_URL = "http://s2.91sgc.rocks/pw/thread.php?fid=3"

DOWN_FLODERS = r"\\192.168.31.201\Datas\Bad_Item\Torrent_By_1024\00.Collection"

POST_ROOT_URL = "http://s2.91sgc.rocks/pw"

headers = { 'User-Agent' : " 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'" }

def main():

    gmm = Get_1024_MagnetLink_Main(mysqlConn, ROOT_URL, DOWN_FLODERS, POST_ROOT_URL, headers)

    tableName = "craw_page_flag"
    # gmm.Get_All_Post_Url(tableName)

    for page in range(1, 5):

        subPageUrl = "{0}&page={1}".format(ROOT_URL, page)
        print("获取第{0}页帖子列表链接 {1}".format(page, subPageUrl))

        html = requests.get(url=subPageUrl, params=headers)
        html = html.content.decode('utf-8', 'ignore')
        soup = BeautifulSoup(html, 'html.parser')

        # mainDivContant = soup.find_all(name="tr", attrs={"class": "tr3 t_one", "align": "center"})
        mainDivContant = soup.find_all("a", attrs={"id":re.compile("a_ajax_\d+")})



        for subNode in mainDivContant:

            postNode, whereDict = Rtn_Post_Info(subNode)

            if len(postNode) != 0 :

                # print(postNode, whereDict)

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

                    print(downSubFloder)
                    isExists = os.path.exists(downSubFloder)
                    if not isExists:
                        # 如果不存在则创建目录
                        os.makedirs(downSubFloder)

                    rtnMsg = gmm.Get_Post_Content_List(tableName, postNode, downSubFloder)

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

                        print()

def Rtn_Post_Info(subNode):

    includeTextFlag = [
        "▲",
        "★",
        "◆",
        "☆",
        "☛",
    ]

    postNode = OrderedDict()

    whereDict = OrderedDict()

    for textFlag in includeTextFlag:

        if textFlag in subNode.text:
            postNode["web_name"] = "1024"

            postNode["title"] = subNode.text
            subUrl = subNode.get("href")
            postNode["id"] = subNode.get("id")
            folderName = "{0}_{1}".format(id, postNode["title"])
            folderName = folderName.replace("\xa0", "")
            postNode["href"] = "{0}/{1}".format(POST_ROOT_URL, subUrl)
            postNode["search_flag"] = "0"
            # print(folderName, postNode["href"])


            whereDict["web_name"] = postNode["web_name"]
            whereDict["id"] = postNode["id"]

            break

    return postNode, whereDict

if __name__ == "__main__":

    main()

