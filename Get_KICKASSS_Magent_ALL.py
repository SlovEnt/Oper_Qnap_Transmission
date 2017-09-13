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


if __name__ == "__main__":
    try:

        paramInfo = Get_Param_In_DB("CRAW_KIC")

        rootUrl = paramInfo["KIC_ROOT_SITE"]

        wait = ui.WebDriverWait(driver, 10)

        driver.get(rootUrl)

        pageSourceScript = driver.page_source

        soup = bs4.BeautifulSoup(pageSourceScript, "html.parser")


        # print(soup)

        # soup.head.children

        urls = soup.find_all('ul', class_="dropdown dp-middle dropdown-msg upper")

        for x in urls:
            print(tmpinfo(),type(x.text))
            print(tmpinfo(),x.text)

        # dataReg = re.compile(
        #     r'''<i class="ka ka16 ka-(.+?) lower"></i>(.+?)</a></li>''')
        #
        # rawDatas = dataReg.findall(urls)
        # print(tmpinfo(),rawDatas)
        # for data in rawDatas:
        #
        #     strSql = "select count(*) from sys_dict where dict_the = 'kic' and dict_id = '%s' and dict_item='%s' and dict_item_sl='%s';" % (data[0],data[1],data[1])
        #     rtnCnt = mysqlExe.ExecQuery(strSql.encode('utf-8'))[0][0]
        #
        #     if rtnCnt == 0:
        #
        #         strSql = "INSERT INTO sys_dict (dict_the, dict_id, dict_item, dict_item_sl, dict_item_spf) VALUES ('kic', '%s', '%s', '%s', '');" % (data[0],data[1],data[1])
        #         print(strSql)
        #         mysqlExe.ExecNonQuery(strSql.encode('utf-8'))


        # wait.until(lambda dr: dr.find_element_by_id('fb-root').is_displayed())

        # print(pageSourceScript)











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









