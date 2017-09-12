import re
import time
import random
import platform
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import selenium.webdriver.support.ui as ui
from multiprocessing import Pool
# import traceback
# from bs4 import BeautifulSoup
# from html.parser import HTMLParser

from Oper_Mysql_Class import *
from PrintFormatLogs import *
from Comm_Func import *

sysType = platform.system()
if sysType == "Windows":
    phantomjsPath = r"..\\phantomjs.exe"
elif sysType == "Linux":
    phantomjsPath = r"/my_workspace/python/phantomjs"
elif sysType == "Darwin":  # mac
    phantomjsPath = r"../phantomjs"

dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap['phantomjs.page.customHeaders.Accept-Language'] = 'en_US'
dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0") #设置user-agent请求头
dcap["phantomjs.page.settings.loadImages"] = False # 禁止加载图片
driver = webdriver.PhantomJS(executable_path=phantomjsPath,desired_capabilities=dcap)

def __Pull_SubUrl_Content(subUrl):

    try:

        driver.get(subUrl)
        pageSourceScript = driver.page_source

        print(pageSourceScript)

        # 取帖子主题名称
        dataReg = re.compile(r'''tid=\d\d\d\d\d\d">(.+?)</a>''')
        rawDatas = dataReg.findall(pageSourceScript)
        if len(rawDatas) != 0:
            magnetName = rawDatas[0]
        else:
            magnetName = ""

        # 取帖子主题发布时间
        dataReg = re.compile(r'''">发表于 (.+?)</em>''')
        rawDatas = dataReg.findall(pageSourceScript)
        if len(rawDatas) != 0:
            upDatetime = rawDatas[0]
        else:
            upDatetime = ""

        dataReg = re.compile(r'''magnet(.+?)br>''') # 提取页面中的磁力链，取出时没有加magnet 后续需要补充相关字符
                              # '''magnet:?xt=urn:btih:52A8A2B51D10CA11B8CC16311301E537FDA47355&amp;NHDTA-590<br>'''
        rawDatas = dataReg.findall(pageSourceScript)

        for data in rawDatas:

            magnet = "magnet" + data  # 回补磁力链字符串头信息

            # 提取磁力链中的 hash_string 和 资源名 信息
            dataReg = re.compile(r'''magnet:\?xt=urn:btih:(.+?)&amp;.+?(.+?)<''')
            magnetDatas = dataReg.findall(magnet)

            # 从磁力链中获取 hash_string 和 资源名等信息 信息

            for magnetInfo in magnetDatas:
                if len(magnetInfo) == 2:

                    hash_string = magnetInfo[0]
                    # print(hash_string)

                    # 格式化magnet字符串 将已知的多余的字符替换为空
                    magnet = magnet.replace("<","").replace("'","")


                    # 格式化资源名
                    rs_name1 = magnetInfo[1].replace("<", "").replace("'", "").replace("dn=", "").replace("n=", "")

                    rs_name = "%s %s" % (magnetName, rs_name1)

                    # print(tmpinfo(),upDatetime, hash_string, rs_name, magnet)

                    strSql = "select count(1) from get_tpb_all_magnet where hash_string = '%s';" % (hash_string)
                    rtnCnt = mysqlExe.ExecQuery(strSql.encode('utf-8'))[0][0]

                    if rtnCnt < 1:

                        insertSQL="INSERT INTO get_tpb_all_magnet (up_datetime, hash_string, up_user, rs_name, rs_category, rs_type, up_size, magnet, down_flag) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (
                            upDatetime, hash_string, "SEX169", rs_name, "Porn", "Movies", "-", magnet, "0"
                        )

                        print (debug(), "%s" % (
                                insertSQL
                            )
                        )

                        mysqlExe.ExecNonQuery(insertSQL.encode('utf-8'))

                    else:
                        print(debug(),"%s 已存在，跳过！" % hash_string)

        return True

    except Exception as e:
        print(e)
        return False



if __name__ == '__main__':


    # __Pull_SubUrl_Content("http://149.56.45.111/bbs/forum.php?mod=viewthread&tid=247740&extra=page%3D1")


    for i in range(1,20):

        rootUrl = "http://149.56.45.111/bbs/forum.php?mod=forumdisplay&fid=159&page=%d" % i
        print(debug(),"RootUrl = %s" % rootUrl)

        driver.get(rootUrl)
        pageSourceScript = driver.page_source
        # print(pageSourceScript)

        dataReg = re.compile(r'''<td class="icn">\n<a href="(.+?)" title=".+?" target="_blank">\n''')
        rawDatas = dataReg.findall(pageSourceScript)

        for data in rawDatas :

            subUrl = "http://149.56.45.111/bbs/" + data.replace("amp;","")
            print(debug(),"SubUrl = %s" % subUrl)

            # 取url连接ID
            dataReg = re.compile(r'''http://149.56.45.111/bbs/forum.php\?mod=viewthread&tid=(.+?)&extra=page''')
            rawDatas = dataReg.findall(subUrl)

            search_flag = 0
            if len(rawDatas) != 0:
                subUrlId = rawDatas[0]
                # print(tmpinfo("subUrlId"),subUrlId)

                strSql = "select count(*) from sex169_search_id where id = '%s'" % subUrlId
                search_flag = mysqlExe.ExecQuery(strSql.encode('utf-8'))[0][0]

                if search_flag == 0 :

                    pullFlag = __Pull_SubUrl_Content(subUrl)

                    strSql = "insert into sex169_search_id (id, search_flag,url) VALUES ('%s', '%s','%s');" % (subUrlId, "1",subUrl)
                    mysqlExe.ExecNonQuery(strSql.encode('utf-8'))

                else:
                    print(debug(),"跳过 ID='%s' 的帖子！" % subUrlId)

