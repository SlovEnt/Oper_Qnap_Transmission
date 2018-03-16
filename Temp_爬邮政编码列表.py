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

def GetAreaInfo(cityInfo):
    provinceInfoArr = []
    provinceInfoDict = {}

    rootUrl = "http://tool.cncn.com"
    # print("%s%s" % (rootUrl,cityInfo[0]))

    subUrl = "%s%s" % (rootUrl, cityInfo[0])

    # 补充新增字段信息，一次完成，后续无需使用
    # strSql = "select city_name from `v2PySql`.`provnce_flag`  where url = '%s'" % (subUrl)
    # cityNmae = mysqlExe.ExecQuery(strSql)
    # if len(cityNmae) != 0 :
    #     if cityNmae[0][0] == None :
    #         strSql = "update `v2PySql`.`provnce_flag`  set city_name='%s' where url = '%s'" % (cityInfo[1], subUrl)
    #         mysqlExe.ExecNonQuery(strSql)

    strSql = "select flag from `v2PySql`.`provnce_flag`  where url = '%s'" % (subUrl)

    while True:
        try:
            rtnDatas = mysqlExe.ExecQuery(strSql)
            break
        except Exception as e:
            print(e)
            time.sleep(1)

    if str(len(rtnDatas)) == "0":
        rtnCnt = "2"
    else:
        rtnCnt = rtnDatas[0][0]

    if rtnCnt == "2":
        print("新增城市名为 %s %s 的数据！" % (cityInfo[1], cityInfo[0]))
        strSql = "INSERT INTO `v2PySql`.`provnce_flag` (`city_name`, `url`, `flag`) VALUES ('%s', '%s', '0');" % (cityInfo[1], subUrl)
        print(strSql)

        while True:
            try:
                mysqlExe.ExecNonQuery(strSql)
                break
            except Exception as e:
                print(e)
                time.sleep(1)

    if rtnCnt != "1" :

        req = request.Request("%s%s" % (rootUrl, cityInfo[0]), headers=head)
        while True:
            try:
                response = request.urlopen(req)
                break
            except Exception as e:
                print(e)
                time.sleep(10)
        html = response.read().decode('gbk')
        soup = BeautifulSoup(html, "html.parser")

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

        if len(source) > 1:

            sourceSub = source[1].find_all("a", href=True)

            for x in sourceSub:

                if x.get_text(strip=True):

                    # print(x['href'])
                    provinceInfoDict["postCode"] = x.text
                    provinceInfoDict["provinceName"] = provinceName
                    provinceInfoDict["cityName"] = cityInfo[1]
                    provinceInfoDict["areaCode"] = areaCode

                    strSql = "select count(*) from `v2PySql`.`province_info` where post_code = '%s'" % (provinceInfoDict["postCode"])
                    while True:
                        try:
                            rtnCnt = mysqlExe.ExecQuery(strSql)[0][0]
                            break
                        except Exception as e:
                            print(e)
                            time.sleep(1)

                    if rtnCnt == 0:
                        streetUrl = "%s%s" % ("http://tool.cncn.com", x['href'])
                        req = request.Request(streetUrl, headers=head)

                        while True:
                            try:
                                response = request.urlopen(req)
                                break
                            except Exception as e:
                                print(e)
                                time.sleep(10)

                        streetUrlHtml = response.read().decode('gbk')
                        time.sleep(2)

                        streetUrlHtmlPage = BeautifulSoup(streetUrlHtml, "html.parser")
                        # print(streetUrlHtmlPage)
                        source = streetUrlHtmlPage.find_all(class_='txt_area')[0].find_all("li")

                        for d in source:
                            provinceInfoDict["address"] = d.text

                            # print(provinceInfoDict)

                            strSql = '''INSERT INTO `v2PySql`.`province_info` (`province`, `city`, `area_name`, `area_code`, `post_code`, `address`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s');''' % (
                                provinceName,
                                cityInfo[1],
                                '',
                                areaCode,
                                provinceInfoDict["postCode"],
                                provinceInfoDict["address"]
                            )
                            while True:
                                try:
                                    print(strSql)
                                    mysqlExe.ExecNonQuery(strSql)
                                    break
                                except Exception as e:
                                    print(e)
                                    time.sleep(1)

                    else :

                        print("%s 已经存在 %s 条记录，跳过！" % (provinceInfoDict["postCode"], rtnCnt) )

                    provinceInfoDict = {}

        strSql = "update `v2PySql`.`provnce_flag` set flag = '1' where `url`= '%s';" % (subUrl)
        while True:
            try:
                mysqlExe.ExecNonQuery(strSql)
                break
            except Exception as e:
                print(e)
                time.sleep(1)

        time.sleep(5)

    else:
        print("城市名为 %s %s 的地址已爬取完成，忽略！" % (cityInfo[1], cityInfo[0]))


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
