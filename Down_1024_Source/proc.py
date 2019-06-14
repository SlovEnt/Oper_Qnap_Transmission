# -*- coding: utf-8 -*-
__author__ = 'SlovEnt'
__date__ = '2019/6/6 21:46'

from bs4 import BeautifulSoup
import requests
from collections import OrderedDict
import re
import os
import traceback
import random
import time
import json
import random,string
from selenium import webdriver
from ResPacks.UsedCommFuncs import Get_Param_Info

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 参数加载区
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG_FILE = "{0}/Config.ini".format(BASE_DIR)
globParaList = Get_Param_Info(CONFIG_FILE)


CHROME_PATH = globParaList["CHORME_PATH"]

SAVE_SCREE_FILE = r"screenshots"

chromeOptions = webdriver.ChromeOptions()
chromeOptions.binary_location = r"{0}\{1}".format(CHROME_PATH, "chrome.exe")
chromeDriver = r"{0}\{1}".format(CHROME_PATH, "chromedriver.exe")
chromeOptions.add_argument('--headless')
chromeOptions.add_argument('--disable-gpu')

class Get_1024_MagnetLink_Main():

    def __init__(self, mysqlConn, ROOT_URL, DOWN_FLODERS, POST_ROOT_URL):
        self.mysqlConn = mysqlConn
        self.ROOT_URL = ROOT_URL
        self.DOWN_FLODERS = DOWN_FLODERS
        self.POST_ROOT_URL = POST_ROOT_URL
        self.headers = get_new_headers(ROOT_URL)

    def Table_Row_Is_Exist(self, tableName, whereDict):
        ''' 返回指定条件下返回的ROW数据总数 '''
        strSql = "SELECT * FROM {0} WHERE 0=0".format(tableName)
        strWhere = ""
        for key, value in whereDict.items():
            strWhere = strWhere + " " + "AND {0}='{1}'".format(key, value)

        strSql = strSql + strWhere

        rtnDatas = OrderedDict()

        # print(strSql)
        rtnDBDatas = self.mysqlConn.query(strSql)

        rtnDatas["CNT"] = len(rtnDBDatas)
        rtnDatas["CONTENT"] = rtnDBDatas
        # rtnDatas["STRWHERE"] = strWhere.replace(strWhere[0:4], "")
        rtnDatas["STRSQL"] = strSql

        return rtnDatas

    def Update_Init_TaskLog(self,tableName, whereDict, newSetData):
        ''' 入参格式 第一个字典为条件字典 第二个是SET字段（字典格式） '''

        # 分拆字典 把原始字典分拆为两个SQL语句段 条件 SET
        strWhereSql = ""
        strSetSql = ""
        strQuerySql = ""

        for setField in newSetData:

            # 删除folder_name字典项 数据库中无此列表
            if setField == "folder_name":
                continue

            ''' 组装SET语句 '''
            for key, value in newSetData.items():
                if isinstance(value,str) == True :
                    value = value.replace("'", "''")
                if key == setField:
                    # SET 语句
                    if strSetSql == "":
                        strSetSql = "%s='%s'" % (key, value)
                        strQuerySql = "%s" % (key)
                    else:
                        strSetSql = strSetSql + ", %s='%s'" % (key, value)
                        strQuerySql = strQuerySql + ", %s" % (key)

        for setField in whereDict:
            ''' 组装WHERE语句 '''
            for key, value in whereDict.items():
                if isinstance(value,str) == True :
                    value = value.replace("'", "''")
                if key == setField:
                    # SET 语句
                    if strWhereSql == "":
                        strWhereSql = " AND %s='%s'" % (key, value)
                    else:
                        strWhereSql = strWhereSql + "AND %s='%s'" % (key, value)

        ''' 最终组装UPDATE全语句 '''
        strSql = "UPDATE {0} SET {1} WHERE 0=0{2}".format(tableName, strSetSql, strWhereSql)
        # print(strSql)

        try:
            self.mysqlConn.execute(strSql)
            return True
        except Exception as e:
            print(e)
            return False

    def Inser_Init_TaskLog(self, tableName, postNode):
        fieldList = ""
        valueList = ""
        for key, value in postNode.items():
            if key == "folder_name":
                continue
            if fieldList == "":
                fieldList = "{0}".format(key)
                valueList = "'{0}'".format(value)
            else:
                fieldList = "{0}, {1}".format(fieldList, key)
                valueList = "{0}, '{1}'".format(valueList, value)
        strSql = "INSERT INTO {0} ({1}) VALUES ({2})".format(tableName, fieldList, valueList)
        # print(strSql)
        try:
            self.mysqlConn.execute(strSql)
            return True
        except Exception as e:
            return e

    def Is_Re_Correctly(self, text, regularExp, msg = ""):

        rawDatasOne = regularExp.findall(text)

        if len(rawDatasOne) == 0 :
            return False
        else :

            # for data in rawDatasOne :
            #     print("匹配 {0}".format(msg), data)

            return rawDatasOne

    def get_html_all_content(self, url, pageFlag, encode):
        '''
        :param url:  网址
        :param pageFlag: 爬取页面标识（特征，确认正确获取页面）
        :return:
        '''
        # time.sleep(2)
        html = ""
        getFlag = False # 下载结束标志
        proxyFlag = "N" # 代理使用标志
        proxyList = get_proxy_list(self.mysqlConn) # 获取代理列表
        downCnt = 0
        while getFlag == False:

            # 下载10次则直接跳出
            if downCnt >= 10:
                break

            try:
                headers = get_new_headers(url)
                downCnt += 1
                if proxyFlag == "N":
                    r = requests.get(url=url, headers=headers, timeout=30, verify=False)
                    r.raise_for_status()
                    if r.status_code == 200:
                        getFlag == True
                else:
                    for proxyInfo in proxyList:
                        # if downCnt >= 30:
                        #     break
                        print("10998 获取代理", proxyInfo)
                        proxies = {proxyInfo["type"]: '{0}://{1}:{2}'.format(proxyInfo["type"], proxyInfo["ip"], proxyInfo["port"])}
                        try:
                            r = requests.get(url=url, headers=headers, timeout=30, verify=False, proxies=proxies)
                            proxyList.pop(0)
                            r.raise_for_status()
                            if r.status_code == 200:
                                getFlag == True
                                break
                        except Exception as e:
                            print(10057, url, e)
                            strSql = "update proxy_list set weights = weights+1 where ip='{0}' and port='{1}' and type='{2}'".format(proxyInfo["ip"], proxyInfo["port"], proxyInfo["type"])
                            self.mysqlConn.execute(strSql)

                html = r.content.decode(encode, 'ignore')

                if pageFlag != "*" and pageFlag not in html:
                    raise Exception("页面内容获取失败！！")
                else:
                    getFlag = True

            except Exception as e:
                # traceback.print_exc()
                print(10055, url, e)

                # 本地IP尝试下载3次
                if downCnt>3:
                    proxyFlag = "Y"

                print("----------error----------\n{0}\n----------end----------\n".format(html))
                getFlag = False
                time.sleep(5)
        return html

    def down_image(self, url):
        '''
        :param url:  网址
        :param pageFlag: 爬取页面标识（特征，确认正确获取页面）
        :return:
        '''
        # time.sleep(2)
        html = ""
        getFlag = False # 下载结束标志
        proxyFlag = "N" # 代理使用标志
        proxyList = get_proxy_list(self.mysqlConn) # 获取代理列表
        downCnt = 0
        while getFlag == False:

            # 下载10次则直接跳出
            if downCnt >= 10:
                break

            try:
                headers = get_new_headers(url)
                downCnt += 1
                if proxyFlag == "N":
                    r = requests.get(url=url, headers=headers, timeout=30, verify=False)
                    r.raise_for_status()
                    if r.status_code == 200:
                        getFlag == True
                else:
                    for proxyInfo in proxyList:
                        print("10998 获取代理", proxyInfo)
                        proxies = {proxyInfo["type"]: '{0}://{1}:{2}'.format(proxyInfo["type"], proxyInfo["ip"], proxyInfo["port"])}
                        try:
                            r = requests.get(url=url, headers=headers, timeout=30, verify=False, proxies=proxies)
                            proxyList.pop(0)
                            r.raise_for_status()
                            if r.status_code == 200:
                                getFlag == True
                                break
                            else:
                                print(r.status_code)
                        except Exception as e:
                            print(10057, url, e)
                            strSql = "update proxy_list set weights = weights+1 where ip='{0}' and port='{1}' and type='{2}'".format(proxyInfo["ip"], proxyInfo["port"], proxyInfo["type"])
                            self.mysqlConn.execute(strSql)

            except Exception as e:
                # traceback.print_exc()
                print(10055, url, e)

                # 本地IP尝试下载3次
                if downCnt>3:
                    proxyFlag = "Y"

                # print(html)
                getFlag = False
                time.sleep(5)
        return r

    def down_torrent(self, url):
        '''
        :param url:  网址
        '''
        getFlag = False # 下载结束标志
        proxyFlag = "N" # 代理使用标志
        proxyList = get_proxy_list(self.mysqlConn) # 获取代理列表
        downCnt = 0

        while getFlag == False:

            # 下载10次则直接跳出
            if downCnt >= 10:
                break

            try:

                headers = get_new_headers(url)
                headers["Referer"] = url
                headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
                headers["Accept-Encoding"] = "gzip, deflate"
                headers["Upgrade-Insecure-Requests"] = "1"

                strLetterNum=string.ascii_letters+string.digits

                datas = {
                            "".join(random.sample(strLetterNum, 6)) :"".join(random.sample(strLetterNum, 6)),
                            "".join(random.sample(strLetterNum, 6)) :"".join(random.sample(strLetterNum, 6)),
                            "".join(random.sample(strLetterNum, 6)) :"".join(random.sample(strLetterNum, 6)),
                            "".join(random.sample(strLetterNum, 6)) :"".join(random.sample(strLetterNum, 6)),
                            "".join(random.sample(strLetterNum, 6)) :"".join(random.sample(strLetterNum, 6)),
                         }

                downCnt += 1
                if proxyFlag == "N":
                    r = requests.post(url=url, headers=headers, timeout=30, verify=False, data=json.dumps(datas))
                    r.raise_for_status()
                    if str(r.status_code) == "200":
                        getFlag = True
                else:
                    for proxyInfo in proxyList:
                        print("10998 获取代理", proxyInfo)
                        proxies = {proxyInfo["type"]: '{0}://{1}:{2}'.format(proxyInfo["type"], proxyInfo["ip"], proxyInfo["port"])}
                        try:
                            r = requests.post(url=url, headers=headers, timeout=30, verify=False, proxies=proxies, data=json.dumps(datas))
                            proxyList.pop(0)
                            r.raise_for_status()
                            if str(r.status_code) == "200":
                                getFlag == True
                                break
                        except Exception as e:
                            print(10057, url, e)
                            strSql = "update proxy_list set weights = weights+1 where ip='{0}' and port='{1}' and type='{2}'".format(proxyInfo["ip"], proxyInfo["port"], proxyInfo["type"])
                            self.mysqlConn.execute(strSql)
            except Exception as e:
                # traceback.print_exc()
                print(10055, url, e)

                # 本地IP尝试下载3次
                driver = webdriver.Chrome(executable_path=chromeDriver, chrome_options=chromeOptions)
                browerLength = 1280
                browerWidth = 4096
                driver.set_window_size(browerLength, browerWidth)
                driver.get(url)
                driver.implicitly_wait(30)
                driver.close()
                driver.quit()

                if downCnt>3:
                    proxyFlag = "Y"

                # print("\n----------error------------\n{0}\n------end--------\n".format(r))
                getFlag = False
                time.sleep(5)
        return r

    def down_torrent_and_images(self, subPostHtml, postNode, downSubFloder):

        try:
            downFlag = True

            if subPostHtml == "":
                return False

            if "http://koxzp.com/" in subPostHtml:
                return False

            soup = BeautifulSoup(subPostHtml, 'html.parser')
            nodes = soup.find_all(name="div", attrs={"class":"f14",'id':"read_tpc"})
            nodeContent = str(nodes[0])

            # print("--------\n{0}\n------------".format(nodeContent))

            if "www1.downsx" in nodeContent:
                divNodesList = re.split(""""_blank">http://www1.downsx..+?</a>""", nodeContent)
                del divNodesList[-1]
            elif "hgcdown" in nodeContent:
                divNodesList = re.split(""""_blank">http://www1.hgcdown.+?</a>""", nodeContent)
                del divNodesList[-1]
            elif "uptorrentfilespacedownhostabc" in nodeContent:
                divNodesList = re.split(""""_blank">http://www3.uptorrentfilespacedownhostabc.+?</a>""", nodeContent)
                del divNodesList[-1]
            elif "<br/><br/><br/><br/><br/><br/><br/>" in nodeContent:
                divNodesList = re.split("""<br/><br/><br/><br/><br/><br/><br/>""", nodeContent)
            elif "<br/><br/><br/><br/><br/><br/>" in nodeContent:
                divNodesList = re.split("""<br/><br/><br/><br/><br/><br/>""", nodeContent)
            elif "<br/><br/><br/><br/><br/>" in nodeContent:
                divNodesList = re.split("""<br/><br/><br/><br/><br/>""", nodeContent)
            elif "￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣" in nodeContent:
                divNodesList = re.split("""￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣""", nodeContent)
            elif "--------" in nodeContent:
                divNodesList = re.split("""--------""", nodeContent)
            elif "============" in nodeContent:
                divNodesList = re.split("""============""", nodeContent)
            else:
                print("10778 未找到分割规则！！！")
                raise "10778 未找到分割规则！！！ {0}".format(postNode)

            divNodeCnt = len(divNodesList)
            n = 0 # 单一帖子资源组编号 照片+种子资源为一组
            for divNode in divNodesList:

                if "http" not in divNode:
                    continue

                n += 1
                filePrefix = '%03d' % n
                print("------------------ {0} - {1}/{2} ------------------".format(postNode["id"], filePrefix, '%03d' % divNodeCnt))
                # divNode = divNode.replace("=", "")
                divNode = divNode.replace('<div class"f14" id"read_tpc">', "")
                # divNode = divNode.replace("<br/><br/>", "<br/>")
                # divNode = divNode.replace("<br/><br/>", "<br/>")
                print("10899 {0} 单一影片原始节点信息 {1}".format(postNode["id"], divNode))

                # 从节点中获取所有图片资源链接
                imgPre = re.compile(r"""src="(.+?)"/>""")
                imgLinks = self.Is_Re_Correctly(divNode, imgPre, "图片链接")
                if imgLinks is False:
                    continue

                for imgLink in imgLinks:
                    imgFileName = os.path.basename(imgLink)
                    if "." not in imgFileName:
                        continue
                    imgFullPathFile = "{0}\{3}_{1}_{2}".format(downSubFloder, filePrefix, imgFileName, postNode["id"])
                    print("19885 {0} 开始下载图片 {1}。".format(postNode["id"], imgLink, imgFullPathFile))
                    img = self.down_image(imgLink)
                    with open(imgFullPathFile, "wb") as f:
                        f.write(img.content)

                # 从节点中获取所有种子资源链接
                torrentPre = re.compile(r"""<a href="(.+?)" target=""")
                torrentLinks = self.Is_Re_Correctly(divNode, torrentPre, "种子链接")
                for torrentLink in torrentLinks:

                    if "kccdk.com" in torrentLink:
                        continue

                    if "motelppp" in torrentLink and "downsx" in divNode:
                        '''可能一个节点会有两种BT连接，只取downsx网站的种子'''
                        continue

                    if "movieppp" in torrentLink and "downsx" in divNode:
                        '''可能一个节点会有两种BT连接，只取downsx网站的种子'''
                        continue

                    print("19365 {0} 种子下载链接：{1}".format(postNode["id"], torrentLink))

                    if "downsx" in torrentLink or "vodxxtv" in torrentLink or "hgcdown" in torrentLink:

                        while True:
                            torrent_r = self.down_torrent(torrentLink)
                            text = torrent_r.content.decode('utf-8', 'ignore')
                            torrentDownPre = re.compile(r"""href="(.+?)">下載檔案</a>""")

                            torrentDownExten = self.Is_Re_Correctly(text, torrentDownPre)

                            if torrentDownExten is not False:
                                break
                                # raise "10097 torrentDownExten 未能得到想要的结果！[{0}]".format(text)

                        torrentArr = torrentLink.split("/torrent")

                        newDownLink = "{0}{1}".format(torrentArr[0], torrentDownExten[0])
                        print("19366 {0} 种子真实链接：{1}".format(postNode["id"], newDownLink))

                        torrent = self.down_torrent(newDownLink)
                        torrentFullPathFile = "{0}\{2}_{1}.torrent".format(downSubFloder, filePrefix, postNode["id"])
                        with open(torrentFullPathFile, "wb") as code:
                            code.write(torrent.content)

            downFlag = True

        except Exception as e:
            # print("10899 {0} 单一影片原始节点信息 {1}".format(postNode["id"], divNode))
            traceback.print_exc()
            print(10067, e )
            return False

        return downFlag


    def Get_BBS169_Forum_Contant(self, forumInfo):
        pass

def get_new_headers(url):
    user_agent = [
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
        "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
        "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
        "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
        "Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
        "Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
        "Mozilla/5.0 (Linux; U; Android 2.3.7; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
        "MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
        "Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10",
        "Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13",
        "Mozilla/5.0 (BlackBerry; U; BlackBerry 9800; en) AppleWebKit/534.1+ (KHTML, like Gecko) Version/6.0.0.337 Mobile Safari/534.1+",
        "Mozilla/5.0 (hp-tablet; Linux; hpwOS/3.0.0; U; en-US) AppleWebKit/534.6 (KHTML, like Gecko) wOSBrowser/233.70 Safari/534.6 TouchPad/1.0",
        "Mozilla/5.0 (SymbianOS/9.4; Series60/5.0 NokiaN97-1/20.0.019; Profile/MIDP-2.1 Configuration/CLDC-1.1) AppleWebKit/525 (KHTML, like Gecko) BrowserNG/7.1.18124",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; HTC; Titan)",
        "UCWEB7.0.2.37/28/999",
        "NOKIA5700/ UCWEB7.0.2.37/28/999",
        "Openwave/ UCWEB7.0.2.37/28/999",
        "Mozilla/4.0 (compatible; MSIE 6.0; ) Opera/UCWEB7.0.2.37/28/999",
        # iPhone 6：
        "Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25",

    ]
    headers = {'User-Agent': random.choice(user_agent),
               # 'Host': url,
               # 'referer': url,
               # 'Upgrade-Insecure-Requests': '1',
               # 'Connection': 'Keep-Alive',
               # 'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
               # 'Accept - Encoding': 'gzip, deflate',
               # 'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.5',
               # ':authority': url,
               # ':method': "GET",
               }
    return headers

def get_html_all_content(url, pageFlag, encode):
    '''
    :param url:  网址
    :param pageFlag: 爬取页面标识（特征，确认正确获取页面）
    :return:
    '''
    # time.sleep(2)
    getFlag = False
    while getFlag == False:
        try:
            headers = get_new_headers(url)
            r = requests.get(url=url, headers=headers, timeout=30, verify=False)
            r.raise_for_status()

            html = r.content.decode(encode, 'ignore')

            if pageFlag not in html:
                  raise Exception("页面内容获取失败！！")
            else:
                getFlag = True

        except Exception as e:
            print(url, e)
            # print(html)
            getFlag = False
            time.sleep(5)
    return html

def get_proxy_list(mysqlConn):

    strSql = "SELECT ip, port, type FROM proxy_list WHERE 0=0 and is_ok='Y' order by weights, ip"

    rtnDBDatas = mysqlConn.query(strSql)

    if len(rtnDBDatas) == 0:
        return False
    else:
        return rtnDBDatas


