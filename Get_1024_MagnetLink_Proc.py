# -*- coding: utf-8 -*-
__author__ = 'SlovEnt'
__date__ = '2018/4/30 0:03'

from bs4 import BeautifulSoup
import requests
from collections import OrderedDict
import re
import os
import traceback

class Get_1024_MagnetLink_Main():

    def __init__(self, mysqlConn, ROOT_URL, DOWN_FLODERS, POST_ROOT_URL, headers):
        self.mysqlConn = mysqlConn
        self.ROOT_URL = ROOT_URL
        self.DOWN_FLODERS = DOWN_FLODERS
        self.POST_ROOT_URL = POST_ROOT_URL
        self.headers = headers

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

    #
    # def Get_Page_Movies_Info(self, nodeContent):
    #     ''' 由于帖子页面非规范 所以需要多重规则来匹配 '''
    #     print("帖子内容爬取", nodeContent)
    #     movieInfoArr = []
    #
    #     n = 0
    #
    #     if "www1.downsx" in nodeContent :
    #         nodes = re.split(""""_blank">http://www1.downsx..+?</a>""", nodeContent)
    #
    #         del nodes[-1]
    #         for node in nodes:
    #
    #
    #             node = node.replace("<div class=\"tpc_content\" id=\"read_tpc\">", "")
    #             # node = node.replace("<br/><br/>", "")
    #             node = node.replace("：", "")
    #             node = node.replace(":", "")
    #             node = node.replace("-", "")
    #             node = node.replace("=", "")
    #
    #             print("单一影片信息", node)
    #
    #     # if "影片名称" in nodeContent or "[MP4]" in nodeContent:
    #     #     # print("帖子内容爬取", nodeContent)
    #     #
    #     #     dataReg = re.compile(r'''【影片名|\[MP4\](.+?)"_blank">http://www1.downsx.+?</a>''')
    #     #     rtnDatas = self.Is_Re_Correctly(nodeContent, dataReg)
    #     #
    #     #
    #     #
    #     #     #
    #     #     # if rtnDatas != False :
    #     #     #
    #     #     #     movieInfo = OrderedDict()
    #     #     #     for subNodeOne in rtnDatas:
    #     #     #         print(subNodeOne)
    #     #     #         patt = []
    #     #     #         patt.append(re.compile(r'''称】：(.+?)【'''))
    #     #     #         patt.append(re.compile(r'''\[高清HD\](.+?)<br/>'''))
    #     #     #
    #     #     #         for x in patt :
    #     #     #             movieNameArr = self.Is_Re_Correctly(subNodeOne, x, "影片名称")
    #     #     #             if movieNameArr != False :
    #     #     #                 if len(movieNameArr) == 1:
    #     #     #                     movieInfo["movie_name"] = movieNameArr[0]\
    #     #     #                         .replace("<br/>","")\
    #     #     #                         .replace("?","")\
    #     #     #                         .replace("\\","")
    #     #     #
    #     #     #         # movieInfoArr.append(movieInfo)
    #     #     #
    #     #     #         dataReg = re.compile(r'''<a href="(.+?)" target=''')
    #     #     #         hrefsInfo = self.Is_Re_Correctly(subNodeOne, dataReg)
    #     #     #
    #     #     #         img_href = []
    #     #     #         torrent_href = []
    #     #     #
    #     #     #         for href in hrefsInfo:
    #     #     #             ''' 种子地址和图片链接识别 '''
    #     #     #             if "ososoo.com" in href:
    #     #     #                 ''' 第一种图片下载格式 '''
    #     #     #                 html = requests.get(url=href, params=self.headers)
    #     #     #                 html = html.content.decode('utf-8', 'ignore')
    #     #     #                 soup = BeautifulSoup(html, 'html.parser')
    #     #     #                 nodes = soup.find_all(name="div", attrs={"class": "uk-text-center uk-margin-large-top uk-margin-bottom"})
    #     #     #                 img_href.append(nodes[0].img["src"])
    #     #     #                 # response = requests.get(url=nodes[0].img["src"], params=self.headers)
    #     #     #                 # filename = os.path.basename(nodes[0].img["src"])
    #     #     #                 # testname = "{0}\{}".format(downSubFloder)
    #     #     #                 # with open(testname, "wb") as code:
    #     #     #                 #     code.write(response.content)
    #     #     #
    #     #     #             if "www1.downsx" in href :
    #     #     #                 ''' 第一种种子下载格式 '''
    #     #     #                 torrent_href.append(torrent_href)
    #     #     #
    #     #     #
    #     #     #         movieInfo["img_href"] = img_href
    #     #     #         movieInfo["torrent_href"] = torrent_href
    #     #     #
    #     #     #         movieInfoArr.append(movieInfo)
    #
    #
    #
    #     # elif "" in nodeContent:
    #     #     pass
    #     #
    #     #
    #     return movieInfoArr

    def Access_Url_RtnContent(self, accessType, fileName, url, downUrl = "", data={}):
        x = 0
        while x <= 10:
            try:
                x += 1
                if accessType == "get":
                    response = requests.get(url=url, params=self.headers)
                else :
                    self.headers = {'Referer': "{0}".format(downUrl)}
                    response = requests.post(url, headers=self.headers, data=data, timeout=30)

                contentText = response.content


                if fileName != "" :
                    with open(fileName, "wb") as f:
                        for chunk in response.iter_content(chunk_size=512):
                            if chunk:
                                 f.write(chunk)

                break

            except Exception as e:

                traceback.print_exc()

                print(e)

                # if "[Errno 2] No such file or directory" in str(e):
                #     break

                # return False

        if x > 10 :
            return  False
        else:
            return  contentText

    def Get_Post_PageContent(self, tableName, postNode, downSubFloder):
        pass

    def Get_Post_Content_List(self, tableName, postNode, downSubFloder):

        downFlag = 0
        postUrl = postNode["href"]
        print("获得帖子下载链接", postUrl)

        pageFileName = r"{0}\0000.html".format(downSubFloder)

        # html = self.Access_Url_RtnContent("get", pageFileName, postUrl)

        html = requests.get(url=postUrl, params=self.headers)


        with open(pageFileName, "wb") as code:
            code.write(html.content)

        html = html.content.decode('utf-8', 'ignore')
        soup = BeautifulSoup(html, 'html.parser')

        nodes = soup.find_all(name="div", attrs={"class":"f14",'id':"read_tpc"})

        # print(nodes)

        if len(nodes) > 0:

            nodeContent = str(nodes[0])

            # print("帖子内容爬取", nodeContent)

            print("下载目录设置", downSubFloder)

            n = 0

            if "點擊進入下載" in nodeContent and "pwpan.com" in nodeContent:

                print("规则1")

                nodeContent = "".join(nodeContent.split())

                divNodesList = re.split("""============""", nodeContent)
                # divNodes = nodeContent.split(""""uptorrentfilespacedownhostabc""")

                for divNode in divNodesList:

                    print("单一影片信息", divNode)


                    n += 1
                    filePrefix = '%03d' % n

                    print("本次文件序号为", filePrefix)

                    # 从节点中获取所有图片资源链接
                    imgPre = re.compile(r"""src="(.+?)"/>""")
                    imgLinks = self.Is_Re_Correctly(divNode, imgPre, "图片链接")
                    if imgLinks != False :
                        for imgsLink in imgLinks :
                            print("开始下载图片", imgsLink)
                            filename = os.path.basename(imgsLink)
                            testname = "{0}\{1}_{2}".format(downSubFloder, filePrefix, filename)
                            while True :
                                try :

                                    response = requests.get(url=imgsLink, params=self.headers)
                                    with open(testname, "wb") as code:
                                        code.write(response.content)
                                    break

                                except Exception as e:
                                    print(e)
                                    if "No such file or directory" in str(e):
                                        break

                        # 从节点中获取所有种子资源链接
                        torrentPre = re.compile(r"""<ahref="(.+?)"target="_blank">""")
                        torrentLinks = self.Is_Re_Correctly(divNode, torrentPre, "种子链接")
                        for torrentLink in torrentLinks:

                            if "www1.downsx" in torrentLink or "adns2.vodxxtv" in torrentLink :

                                while True :

                                    try :
                                        self.headers = {'Referer': "{0}".format(torrentLink)}
                                        response = requests.post(url=torrentLink, params=self.headers, timeout=30)

                                        text = response.content.decode('utf-8', 'ignore')

                                        torrentDownPre = re.compile(r"""href="(.+?)">下載檔案</a>""")
                                        torrentDownExten = self.Is_Re_Correctly(text, torrentDownPre)

                                        torrentArr = torrentLink.split("/torrent")
                                        newDownLink = "{0}{1}".format(torrentArr[0], torrentDownExten[0])

                                        print("剥离下载链接：", torrentLink)
                                        print("实际下载链接：", newDownLink)

                                        response = requests.post(newDownLink, headers=self.headers, timeout=30)
                                        testname = "{0}\{1}.torrent".format(downSubFloder, filePrefix)
                                        with open(testname, "wb") as code:
                                            code.write(response.content)
                                        downFlag += 1
                                        break

                                    except Exception as e :
                                        print(e)

                            elif "qqxbt." in torrentLink:

                                while True:

                                    try:
                                        self.headers = {'Referer': "{0}".format(torrentLink)}
                                        response = requests.post(url=torrentLink, params=self.headers, timeout=30)

                                        text = response.content.decode('utf-8', 'ignore')

                                        # torrentDownPre = re.compile(r"""location.href='(.+?)';this.disabled = true;""")
                                        # torrentDownExten = self.Is_Re_Correctly(text, torrentDownPre)

                                        newDownLink = torrentLink.replace("Public", "Download")
                                        # newDownLink = "{0}{1}".format(torrentArr[0], torrentDownExten[0])

                                        print("剥离下载链接：", torrentLink)
                                        print("实际下载链接：", newDownLink)

                                        response = requests.post(newDownLink, headers=self.headers, timeout=30)
                                        testname = "{0}\{1}.torrent".format(downSubFloder, filePrefix)
                                        with open(testname, "wb") as code:
                                            code.write(response.content)
                                        downFlag += 1
                                        break

                                    except Exception as e:

                                        print(e)
                                        if "No such file or directory" in str(e):

                                            break



            elif "www1.downsx" in nodeContent or "qqxbt." in nodeContent:

                nodes = re.split(""""_blank">http://www1.downsx..+?</a>""", nodeContent)

                del nodes[-1]
                for node in nodes:
                    # node = node.replace("<div class=\"tpc_content\" id=\"read_tpc\">", "")
                    # node = node.replace("<br/><br/>", "")
                    # node = node.replace("：", "")
                    # node = node.replace(":", "")
                    # node = node.replace("-", "")
                    # node = node.replace("=", "")

                    print("单一影片信息", node)

                    n += 1
                    filePrefix = '%03d' % n

                    print("本次文件序号为", filePrefix)

                    # 从节点中获取所有图片资源链接
                    imgPre = re.compile(r"""src="(.+?)"/>""")
                    imgLinks = self.Is_Re_Correctly(node, imgPre, "图片链接")
                    if imgLinks != False :
                        for imgsLink in imgLinks :
                            print("开始下载图片", imgsLink)
                            filename = os.path.basename(imgsLink)
                            testname = "{0}\{1}_{2}".format(downSubFloder, filePrefix, filename)
                            while True :
                                try :

                                    response = requests.get(url=imgsLink, params=self.headers)
                                    with open(testname, "wb") as code:
                                        code.write(response.content)
                                    break

                                except Exception as e:
                                    print(e)
                                    if "No such file or directory" in str(e):
                                        break

                        # 从节点中获取所有种子资源链接
                        torrentPre = re.compile(r"""<a href="(.+?)" target=""")
                        torrentLinks = self.Is_Re_Correctly(node, torrentPre, "种子链接")
                        for torrentLink in torrentLinks:

                            if "www1.downsx" in torrentLink or "adns2.vodxxtv" in torrentLink :

                                while True :

                                    try :
                                        self.headers = {'Referer': "{0}".format(torrentLink)}
                                        response = requests.post(url=torrentLink, params=self.headers, timeout=30)

                                        text = response.content.decode('utf-8', 'ignore')

                                        torrentDownPre = re.compile(r"""href="(.+?)">下載檔案</a>""")
                                        torrentDownExten = self.Is_Re_Correctly(text, torrentDownPre)

                                        torrentArr = torrentLink.split("/torrent")
                                        newDownLink = "{0}{1}".format(torrentArr[0], torrentDownExten[0])

                                        print("剥离下载链接：", torrentLink)
                                        print("实际下载链接：", newDownLink)

                                        response = requests.post(newDownLink, headers=self.headers, timeout=30)
                                        testname = "{0}\{1}.torrent".format(downSubFloder, filePrefix)
                                        with open(testname, "wb") as code:
                                            code.write(response.content)
                                        downFlag += 1
                                        break

                                    except Exception as e :
                                        print(e)

                            elif "qqxbt." in torrentLink:

                                while True:

                                    try:
                                        self.headers = {'Referer': "{0}".format(torrentLink)}
                                        response = requests.post(url=torrentLink, params=self.headers, timeout=30)

                                        text = response.content.decode('utf-8', 'ignore')

                                        # torrentDownPre = re.compile(r"""location.href='(.+?)';this.disabled = true;""")
                                        # torrentDownExten = self.Is_Re_Correctly(text, torrentDownPre)

                                        newDownLink = torrentLink.replace("Public", "Download")
                                        # newDownLink = "{0}{1}".format(torrentArr[0], torrentDownExten[0])

                                        print("剥离下载链接：", torrentLink)
                                        print("实际下载链接：", newDownLink)

                                        response = requests.post(newDownLink, headers=self.headers, timeout=30)
                                        testname = "{0}\{1}.torrent".format(downSubFloder, filePrefix)
                                        with open(testname, "wb") as code:
                                            code.write(response.content)
                                        downFlag += 1
                                        break

                                    except Exception as e:

                                        print(e)
                                        if "No such file or directory" in str(e):

                                            break



                            else:
                                pass

                        # end for

                    # end for

            elif "uptorrentfilespacedownhostabc" in nodeContent :

                nodes = re.split(""""_blank">http://www3.uptorrentfilespacedownhostabc.+?</a>""", nodeContent)
                del nodes[-1]
                for node in nodes:
                    print("单一影片信息", node)
                    n += 1
                    filePrefix = '%03d' % n

                    print("本次文件序号为", filePrefix)

                    # 从节点中获取所有图片资源链接
                    imgPre = re.compile(r"""src="(.+?)"/>""")
                    imgLinks = self.Is_Re_Correctly(node, imgPre, "图片链接")
                    if imgLinks != False:
                        for imgsLink in imgLinks:
                            print("开始下载图片", imgsLink)
                            filename = os.path.basename(imgsLink)
                            testname = "{0}\{1}_{2}".format(downSubFloder, filePrefix, filename)
                            while True:
                                try:

                                    response = requests.get(url=imgsLink, params=self.headers)
                                    with open(testname, "wb") as code:
                                        code.write(response.content)
                                    break

                                except Exception as e:

                                    print(e)
                                    if "No such file or directory" in str(e):
                                        break

                        # 从节点中获取所有种子资源链接
                        torrentPre = re.compile(r"""<a href="(.+?)" target=""")
                        torrentLinks = self.Is_Re_Correctly(node, torrentPre, "种子链接")
                        for torrentLink in torrentLinks:

                            if "uptorrentfilespacedownhostabc" in torrentLink:

                                # print(torrentLink)

                                while True:

                                    try:
                                        self.headers = {'Referer': "{0}".format(torrentLink)}
                                        response = requests.get(url=torrentLink, params=self.headers, timeout=30)

                                        html = response.content.decode('utf-8', 'ignore')
                                        soup = BeautifulSoup(html, 'html.parser')
                                        inputDicts = soup.find_all(name="input", attrs={"type": "hidden"})
                                        data = {}
                                        for inputDict in inputDicts :
                                            data[inputDict["id"]] = inputDict["value"]

                                        torrentArr = torrentLink.split("/file.php")
                                        newDownLink = "{0}{1}".format(torrentArr[0], "/down.php")

                                        # newDownLink = "http://www3.uptorrentfilespacedownhostabc.pw/updowm/down.php"

                                        print("剥离下载链接：", torrentLink)
                                        print("实际下载链接：", newDownLink, data)

                                        response = requests.post(newDownLink, data = data, headers=self.headers, timeout=30)
                                        testname = "{0}\{1}.torrent".format(downSubFloder, filePrefix)
                                        with open(testname, "wb") as code:
                                            code.write(response.content)
                                        downFlag += 1
                                        break

                                    except Exception as e:
                                        print(e)

                            else:
                                pass

                                # end for

                                # end for




        return downFlag





        # movieInfoArr = self.Get_Page_Movies_Info(nodeContent)
        #
        # print(movieInfoArr)

        #
        #
        # print(nodeContent)
        #
        # if "影片名称" in nodeContent :
        #     dataReg = re.compile(r'''【影片名(.+?)"_blank">http://www1.downsx.club/torrent/.+?</a>''')
        #     rawDatas = dataReg.findall(nodeContent)
        #     for subNode in rawDatas:
        #         print(subNode)
        #         dataReg = re.compile(r'''称】：(.+?)【''').findall(subNode)
        #
        #         if len(dataReg) == 1:
        #             movieName = dataReg[0].replace("<br/>","").replace("?","").replace("\\","")
        #             downSubFloder = "{0}\{1}\{2}".format(self.DOWN_FLODERS, postNode["title"],movieName)
        #             print(downSubFloder)
        #             isExists = os.path.exists(downSubFloder)
        #             if not isExists:
        #                 # 如果不存在则创建目录
        #                 os.makedirs(downSubFloder)
        #
        #         dataReg = re.compile(r'''<a href="(.+?)" target=''').findall(subNode)
        #
        #         for x in dataReg:
        #             if ".jpg" in x :
        #                 '''
        #                 第一种情况
        #                 http://www.69img.com/u/20180419/18130022.jpg?imageView2/0/w/640
        #                 http://www.69img.com/i/?i=u/20180419/18130022.jpg
        #                 '''
        #
        #
        #                 response = requests.get("http://www.69img.com/u/20180419/18130022.jpg?imageView2/0/w/640", self.headers)
        #                 # print(torrfile.content)
        #                 testname = "{0}\sdfds.zip.jpg".format(downSubFloder)
        #                 with open(testname, "wb") as code:
        #                     code.write(response.content)

        # dataReg = re.compile(r'''<a href="(.+?)" target="_blank">''')
        # rawDatas = dataReg.findall(nodeContent)
        #
        # for re1 in rawDatas:
        #     print(re1)

        # for node in nodes:
        #     print(node)
        #     print(node.img)

        print("------------------------------------------------------")
        import time
        # time.sleep(60)

    def Get_BBS169_Forum_Contant(self, forumInfo):
        pass







