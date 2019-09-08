# -*- coding: utf-8 -*-
__author__ = 'SlovEnt'
__date__ = '2019/5/17 8:41'

import random
import requests
import time
import os
from Down_TPB_ALL_Magent.tpb_proc import globParaList

from selenium import webdriver
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# BASE_DIR = os.path.dirname(os.path.dirname(__file__))

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
            # headers["User-Agent"] = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"
            # headers["upgrade-insecure-requests"] = "1"
            # headers["accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
            # headers["accept-language"] = "zh-CN,zh;q=0.9,en;q=0.8"
            # headers["ache-control"] = "max-age=0"

            r = requests.get(url=url, headers=headers, timeout=30, verify=False)
            r.raise_for_status()

            html = r.content.decode(encode, 'ignore')

            if pageFlag not in html:
                  raise Exception("页面内容获取失败！！")
            else:
                getFlag = True

        except Exception as e:
            print(url, e)
            print(html)
            getFlag = False
            time.sleep(5)
    return html

def chrome_get_html_all_content(url, pageFlag, encoding="utf-8"):

    SAVE_SCREE_FILE = globParaList["LOG_FILE_PATH"]

    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.binary_location = globParaList["CHORME_PATH"]
    chromeDriver = globParaList["CHROMEDRIVER_PATH"]
    chromeOptions.add_argument('--headless')
    chromeOptions.add_argument('--disable-gpu')

    driver = webdriver.Chrome(executable_path=chromeDriver, chrome_options=chromeOptions)
    browerLength = 1280
    browerWidth = 4096
    driver.set_window_size(browerLength, browerWidth)

    # time.sleep(2)
    getFlag = False
    while getFlag == False:
        try:
            driver.get(url)
            # time.sleep(10)
            driver.implicitly_wait(30)
            html = driver.page_source
            driver.save_screenshot(r"{0}\ok.png".format(SAVE_SCREE_FILE))

            if pageFlag not in html:
                  raise Exception("页面内容获取失败！！")
            else:
                getFlag = True

        except Exception as e:
            print(r"{0}\error.png".format(SAVE_SCREE_FILE))
            driver.save_screenshot(r"{0}\error.png".format(SAVE_SCREE_FILE))
            print(url, e)
            getFlag = False
            time.sleep(5)

        driver.close()
        driver.quit()

    return html

def get_html_all_content_proxy(url, pageFlag, encode, proxyInfoDict):
    '''
    :param url:  网址
    :param pageFlag: 爬取页面标识（特征，确认正确获取页面）
    :return:
    '''
    # time.sleep(2)
    getFlag = False
    n = 0
    html = "-----------------"
    while getFlag == False:
        try:
            n += 1

            headers = get_new_headers(url)

            proxies = {proxyInfoDict["type"]: '{0}://{1}:{2}'.format(
                proxyInfoDict["type"],
                proxyInfoDict["ip"],
                proxyInfoDict["port"]
            )}
            # print(proxies)
            r = requests.get(url=url, headers=headers, timeout=30, verify=False, proxies=proxies)
            # r = requests.get(url=url, headers=headers, timeout=30, verify=False)
            r.raise_for_status()

            html = r.content.decode(encode, 'ignore')

            if pageFlag not in html:
                  raise Exception("页面内容获取失败！！")
            else:
                getFlag = True

        except Exception as e:
            print(url, e)
            print(html)
            if n > 3 :
                getFlag = False
                time.sleep(5)
            else:
                getFlag = True
    return html




