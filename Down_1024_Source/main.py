# -*- coding: utf-8 -*-
__author__ = 'SlovEnt'
__date__ = '2019/6/6 21:45'

import time
import os
import re
import shutil
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
from ResPacks import torndb
from ResPacks.UsedCommFuncs import Get_Param_Info
from proc import get_html_all_content, Get_1024_MagnetLink_Main
import traceback


# 参数加载区
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG_FILE = "{0}/Config.ini".format(BASE_DIR)
globParaList = Get_Param_Info(CONFIG_FILE)

# 引入mysql操作函数
mysqlConn = torndb.Connection(
    "{0}:{1}".format(globParaList["DB_HOST"],globParaList["DB_PORT"]),
    globParaList["DB_NAME"],
    globParaList["USER_NAME"],
    globParaList["USER_PWD"],
)

# 域名
DOMIN_NAME = "http://k6.csnjcbnxdnb.pw"

# 最新合集版块首页
ROOT_URL = "{0}/pw/thread.php?fid=3".format(DOMIN_NAME)

# 单一帖子网址前缀
POST_ROOT_URL = "{0}/pw".format(DOMIN_NAME)

# 下载目录
DOWN_FLODERS = globParaList["Down_1024_Floders"]

# 记录帖子下载标志的数据库后台表
tableName = globParaList["Table_Name"]


def main():

    gmm = Get_1024_MagnetLink_Main(mysqlConn, ROOT_URL, DOWN_FLODERS, POST_ROOT_URL)

    # 下载的最大帖子列表页数
    postsMaxNum = 3

    # 定义数组 用于存放帖子信息
    postInfos = []

    # 帖子中包含的特征字符
    includeTextFlag = [
        "▲",
        "★",
        "◆",
        "☆",
        "☛",
        "◍",
        "◕",
        "√",
        "✽",
        "脫拉庫",
        "㊣",
    ]

    for page in range(1, postsMaxNum + 1):

        subPageUrl = "{0}&page={1}".format(ROOT_URL, page)
        print("10001 获取第{0}页帖子列表链接 {1}".format(page, subPageUrl))

        html = gmm.get_html_all_content(subPageUrl, "main", "utf-8")
        soup = BeautifulSoup(html, 'html.parser')
        mainDivContant = soup.find_all("a", attrs={"id": re.compile("a_ajax_\d+")})

        for subNode in mainDivContant:

            postNode = OrderedDict()

            for textFlag in includeTextFlag:

                if textFlag not in subNode.text:
                    continue

                postNode["web_name"] = "1024"
                postNode["search_flag"] = "0"

                postNode["title"] = subNode.text.replace(' ','')
                subUrl = subNode.get("href")
                postNode["id"] = subNode.get("id")

                # 目录命名 特殊字符做替换处理
                folderName = "{0} - {1}".format(postNode["id"], postNode["title"])
                folderName = folderName.replace("\xa0", "")
                folderName = folderName.replace("/", ".")

                postNode["href"] = "{0}/{1}".format(POST_ROOT_URL, subUrl)
                postNode["folder_name"] = folderName

                postInfos.append(postNode)
                # 如果匹配上 则直接跳出循环 否则下一次匹配会重复加入数组
                break

    n = 120000
    for postNode in postInfos:
        # n += 1
        # print(n, postNode)

        # #****************************************
        # # 当单一帖子出现问题 用以下方式过滤
        # if postNode["id"] != "a_ajax_4116754":
        #     continue
        # #****************************************

        # 下载存放目录
        downSubFloder = "{0}\{1}".format(DOWN_FLODERS, postNode["folder_name"])

        whereDict = OrderedDict()
        whereDict["web_name"] = postNode["web_name"]
        whereDict["id"] = postNode["id"]

        rtnDatas = gmm.Table_Row_Is_Exist(tableName, whereDict)

        if rtnDatas["CNT"] == 0:
            rtnMsg = gmm.Inser_Init_TaskLog(tableName, postNode)

        whereDict["search_flag"] = "1"
        rtnDatas = gmm.Table_Row_Is_Exist(tableName, whereDict)

        if rtnDatas["CNT"] == 1:
            print("10096 id = {0} 帖子标题 = {1} 已经完成下载，无需重复下载！！".format(postNode["id"], postNode["title"]))
            continue

        # 如果不存在则创建目录
        isExists = os.path.exists(downSubFloder)
        if not isExists:
            os.makedirs(downSubFloder)

        # 单一帖子循环下载
        print("10002 下载帖子地址为：{0}，帖子ID为：{1}，帖子标题为：{2}，存放子目录为：{3}。".format(
            postNode["href"],
            postNode["id"],
            postNode["title"],
            downSubFloder,
        ))
        subPostHtml = gmm.get_html_all_content(postNode["href"], "td_tpc", "utf-8")

        # 保存帖子网页内容
        pageFileName = r"{0}\{1}.html".format(downSubFloder, postNode["id"])
        with open(pageFileName, "w", encoding='utf-8') as f:
            f.write(subPostHtml)

        rtnMsg = gmm.down_torrent_and_images(subPostHtml, postNode, downSubFloder)

        whereDict = {}
        whereDict["web_name"] = postNode["web_name"]
        whereDict["id"] = postNode["id"]

        if rtnMsg is False:
            print("10044 下载帖子地址为：{0}，帖子ID为：{1}，帖子标题为：{2}，因某些原因导致下载失败。".format(
                postNode["href"],
                postNode["id"],
                postNode["title"],
            ))
            shutil.rmtree(downSubFloder)
            postNode["search_flag"] = "2"

        else:
            print("10044 下载帖子地址为：{0}，帖子ID为：{1}，帖子标题为：{2}，下载成功。".format(
                postNode["href"],
                postNode["id"],
                postNode["title"],
            ))
            postNode["search_flag"] = "1"

        gmm.Update_Init_TaskLog(tableName, whereDict, postNode)
        print("\n")


# print("10002 下载帖子地址为：{0}，存放子目录为：{1}。".format(postNode["href"], folderName))

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        # traceback.print_exc()