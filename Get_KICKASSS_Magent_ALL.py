import re
import time
import random
import requests
import urllib.request
import urllib
import http.cookiejar
import bs4
import platform
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import selenium.webdriver.support.ui as ui
from multiprocessing import Pool
import traceback


from Comm_Func import *
from Oper_Mysql_Class import *

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


def __Get_KIS_Dict2DB(soup):

    urls = soup.find_all('ul', class_="dropdown dp-middle dropdown-msg upper")

    for url in urls:
        for urlLine in url:
            if urlLine != "\n":
                urlLine = str(urlLine)
                dataReg = re.compile(
                    r'''<li class="topMsg"><a href="/(.+?)/"><i class="ka ka16 ka-.+?"></i>(.+?)</a></li>''')
                rawDatas = dataReg.findall(urlLine)

                for data in rawDatas:

                    strSql = "select count(*) from sys_dict where dict_the = 'kic' and dict_id = '%s' and dict_item='%s' and dict_item_sl='%s';" % (
                    data[0], data[1], data[1])
                    rtnCnt = mysqlExe.ExecQuery(strSql.encode('utf-8'))[0][0]

                    if rtnCnt == 0 and data[0] != "new":
                        strSql = "INSERT INTO sys_dict (dict_the, dict_id, dict_item, dict_item_sl, dict_item_spf) VALUES ('kic', '%s', '%s', '%s', '');" % (
                        data[0], data[1], data[1])
                        print(strSql)
                        mysqlExe.ExecNonQuery(strSql.encode('utf-8'))

def __Get_Kic_Dict(rs_group):
    if rs_group == "ALL":
        sqlStr = "select dict_id from sys_dict where dict_the = 'kic';"
    else:
        sqlStr = "select dict_id from sys_dict where dict_the = 'kic' and dict_item = '"+rs_group+"';"
    listDatas = mysqlExe.ExecQuery(sqlStr.encode('utf-8'))
    groupList = []
    for singData in listDatas:
        groupList.append(singData[0])
    return groupList

def isElementExist(driver):
    try:
        driver.find_element_by_xpath('//*[@id="confirm_age"]/div/div[2]/form/button/span').is_displayed()
        return True
    except:
        return False

def __Down_KIS_Magent_Info(subUrl):

    driver.get(subUrl)

    # <button type="submit" class="siteButton bigButton"><span>Yes, let me see it</span></button>
    yesButton = '''//*[@id="confirm_age"]/div/div[2]/form/button/span'''
    if isElementExist(yesButton) == True:
        driver.find_element_by_xpath(yesButton).click()

    pageSourceScript = driver.page_source
    # print(pageSourceScript)
    print("-----------------------------------------------------------------------")
    soup = bs4.BeautifulSoup(pageSourceScript, "html.parser")
    tr_id_Regexp = re.compile("torrent_\w+_torrents\d+")

    childNodes = soup.find_all("tr", attrs={"id":tr_id_Regexp});

    for childNode in childNodes:
        print(tmpinfo(),childNode)
        # print(tmpinfo(),x.text)



if __name__ == "__main__":
    try:

        # 取本爬虫需要的相关字典信息
        paramInfo = Get_Param_In_DB("CRAW_KIC")
        rootUrl = paramInfo["KIC_ROOT_SITE"]

        # driver.get(rootUrl)
        # pageSourceScript = driver.page_source
        # soup = bs4.BeautifulSoup(pageSourceScript, "html.parser")
        # __Get_KIS_Dict2DB(soup) # 从网站爬字典项

        subUrls = __Get_Kic_Dict("XXX")

        # 启动爬虫进程
        for subUrl in subUrls:
            subUrl = "%s/%s/" % (rootUrl, subUrl)
            __Down_KIS_Magent_Info(subUrl)











        # session = requests.Session()


        # headers = {
        #     'Host': 'kickasss.to' ,
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0',
        #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        #     'Accept-Language':'en-US,en;q=0.8',
        #     'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        #     'Accept-Encoding': 'none',
        #     'Proxy-Connection': 'keep-alive',
        #     'Upgrade-Insecure-Requests':'1',
        #     'Referer': 'http://kickasss.to/xxx/'
        # }  # 虚拟主机头信息
        #
        # # session.get(rootUrl)
        #
        # cj = http.cookiejar.CookieJar()
        # pro = urllib.request.HTTPCookieProcessor(cj)
        # opener = urllib.request.build_opener(pro)
        #
        # request = urllib.request.Request(url=rootUrl, headers=headers)
        # request = urllib.request.urlopen(request)
        #
        # content = request.read().decode("utf-8", "ignore")  # 读取，一般会在这里报异常
        # token = request(content)
        # request.close()  # 记得要关闭
        # print(content)



    except Exception as e:
        print(e)









