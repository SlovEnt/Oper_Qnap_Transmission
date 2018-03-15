#!/usr/bin/python
# coding: UTF-8
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
from urllib import request
import re
import time

from Comm_Func import Get_Param_Info

from Oper_Mysql_Class import MySQL

paramInfo = Get_Param_Info("Config.ini")

# 引入mysql操作函数
mysqlExe = MySQL(
    host = paramInfo["DB_HOST"],
    user = paramInfo["USER_NAME"],
    pwd = paramInfo["USER_PWD"],
    db = paramInfo["DB_NAME"],
    port = int(paramInfo["DB_PORT"])
)

head = {}
head['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36'

def getContent(url):
    req = Request(url)
    # 增加header头信息
    req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36')
    try:
        response = urlopen(req)
        buff = response.read()
        html = buff.decode("utf8")
        response.close()
    except HTTPError as e:
        print('The server couldn\'t ful ll the request.')
        print('Error code: ', e.code)
    except URLError as e:
        print('reason:%s' % e.reason)
    return html


def saveContent(content, url):
    soup = BeautifulSoup(content, "html.parser")
    for link in soup.find("dl", {"id": "dir"}).find_all('a'):
        title = link.get_text()
        url = "http://www.99lib.net" + link.get("href")
        print("title：%s" % title)
        print("url：%s" % url)
        html = getContent(url)
        soup2 = BeautifulSoup(html, "html.parser")
        content = soup2.find("div", {"id": "content"}).get_text()
        print("content:%s" % content)


def GetAreaInfo(cityInfo):
    provinceInfoArr = []
    provinceInfoDict = {}

    rootUrl = "http://tool.cncn.com"
    # print("%s%s" % (rootUrl,cityInfo[0]))

    subUrl = "%s%s" % (rootUrl, cityInfo[0])

    strSql = "select flag from `v2PySql`.`provnce_flag`  where url = '%s'" % (subUrl)

    if str(len(mysqlExe.ExecQuery(strSql))) == "0":
        rtnCnt = "2"
    else:
        rtnCnt = mysqlExe.ExecQuery(strSql)[0][0]

    print(rtnCnt,strSql)

    if rtnCnt != "1" :

        if rtnCnt == "2":
            strSql = "INSERT INTO `v2PySql`.`provnce_flag` (`url`, `flag`) VALUES ('%s', '0');" % (subUrl)
            mysqlExe.ExecNonQuery(strSql)

        req = request.Request("%s%s" % (rootUrl, cityInfo[0]), headers=head)
        response = request.urlopen(req)
        html = response.read().decode('gbk')
        soup = BeautifulSoup(html, "html.parser")
        # source = soup.find_all(class_='select J_select')
        # print(str(soup))



        # provinceResMTR = '''"</sub>\n<a href="/youbian/.+?">(.+?)邮编</a>\n<sub>'''
        # provinceName = re.findall(res_tr, str(soup), re.S | re.M)
        # print(provinceName)
        provinceResMTR = r'''new PCAS\('location_p', 'location_c', 'location_a', '(.+?)', '.+?', ''\)'''
        provinceName = re.findall(provinceResMTR, str(soup), re.S | re.M)[0]

        areaCodeResMTR = r'''<a href=".+?">.+?区号</a>：<b><a href="/quhao/(.+?)">.+?</a></b></p> </div>'''
        areaCodeArr = re.findall(areaCodeResMTR, str(soup), re.S | re.M)
        if len(areaCodeArr) == 1:
            areaCode = areaCodeArr[0]
        else:
            areaCode = 0
        # print(areaCode)

        source = soup.find_all(class_='txt_con')
        # print(source[1])
        sourceSub = source[1].find_all("a", href=True)

        for x in sourceSub:

            if x.get_text(strip=True):

                # print(x['href'])
                provinceInfoDict["postCode"] = x.text
                provinceInfoDict["provinceName"] = provinceName
                provinceInfoDict["cityName"] = cityInfo[1]
                provinceInfoDict["areaCode"] = areaCode

                strSql = "select count(*) from `v2PySql`.`province_info` where post_code = '%s'" % (provinceInfoDict["postCode"])
                rtnCnt = mysqlExe.ExecQuery(strSql)[0][0]

                if rtnCnt == 0:
                    streetUrl = "%s%s" % ("http://tool.cncn.com", x['href'])
                    req = request.Request(streetUrl, headers=head)
                    response = request.urlopen(req)
                    streetUrlHtml = response.read().decode('gbk')
                    streetUrlHtmlPage = BeautifulSoup(streetUrlHtml, "html.parser")
                    # print(streetUrlHtmlPage)
                    source = streetUrlHtmlPage.find_all(class_='txt_area')[0].find_all("li")
                    for d in source:
                        provinceInfoDict["address"] = d.text

                        # print(provinceInfoDict)

                        strSql = "INSERT INTO `v2PySql`.`province_info` (`province`, `city`, `area_name`, `area_code`, `post_code`, `address`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s');" % (
                            provinceName,
                            cityInfo[1],
                            '',
                            areaCode,
                            provinceInfoDict["postCode"],
                            provinceInfoDict["address"]
                        )
                        print(strSql)
                        mysqlExe.ExecNonQuery(strSql)


                    time.sleep(5)
                else :
                    print("%s 已经存在 %s 条记录，跳过！" % (provinceInfoDict["postCode"], rtnCnt) )

                provinceInfoDict = {}

        strSql = "update `v2PySql`.`provnce_flag` set flag = '1' where `url`= '%s';" % (subUrl)
        mysqlExe.ExecNonQuery(strSql)

        time.sleep(5)


if __name__ == "__main__":

    # proxy_support = request.ProxyHandler({'http': '123.206.75.213:8080'})
    # opener = request.build_opener(proxy_support)
    # request.install_opener(opener)

    req = request.Request("http://tool.cncn.com/youbian/", headers=head)
    response = request.urlopen(req)
    html = response.read().decode('gbk')
    # print(html)

    soup = BeautifulSoup(html, "html.parser")
    source = soup.find_all(class_='txt_city a_z')[0]
    # print(type(str(source)))
    # for k in soup.find_all('a'):
    #     print(k)

    res_tr = r'<a href="(.+?)">(.+?)</a>'
    m_tr = re.findall(res_tr, str(source), re.S | re.M)

    for cityInfo in m_tr:
        rtnInfo = GetAreaInfo(cityInfo)
        # print(cityInfo)


