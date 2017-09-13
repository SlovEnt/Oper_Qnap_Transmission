import re
import time
import random
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

def Down_TPB_Magent_Info(singCategory):

    # 获取采集站点域名 统一从库中获取
    siteWeb = Get_Mian_Site_Info("The Pirate Bay")

    wait = ui.WebDriverWait(driver, 10)

    for i in range(0,10):

        enterHttpUrl = siteWeb + "/browse/%s/%d/3" % (singCategory,i)

        # print (debug(),"开始处理分类为%s的第%d页数据: %s" % (singCategory,i,enterHttpUrl))

        driver.get(enterHttpUrl)
        result = isElementExist(driver)

        pageSourceScript = driver.page_source

        if result == True:
            break
        elif "No hits" in pageSourceScript:
            break
        else:
            wait.until(lambda dr: dr.find_element_by_id('foot').is_displayed())
            time.sleep(3)
            # driver.save_screenshot('.\\screen\\screen_out_' + str(i) + '.png')
            rnInPage = 0
            dataReg = re.compile(r'''<td class="vertTh">\W+<center>\W+<a href="/browse/\d+" title="More from this category">(.+?)</a><br>\W+\(<a href="/browse/\d+" title="More from this category">(.+?)</a>\)\W+</center>\W+</td>\W+<td>\W+<div class="detName">\W+<a href=".+?" class="detLink" title="Details for.+?">(.+?)</a>\W</div>\W+<a href="(.+?)" title="Download this torrent using magnet">.+?\W+<font class="detDesc">Uploaded (.+?), Size (.+?), ULed by <a class=.+?>(.+?)</a></font>''')
            rawDatas = dataReg.findall(pageSourceScript)
            for x in rawDatas:
                # 当前页面读取的记录数 最大为30
                rnInPage = rnInPage + 1

                up_user = x[6]
                rs_name = x[2].replace("'", "''").strip() # 资源名称中如果存在单引号 则需要修改为双引号 否则插入sql会报错
                rs_category = x[0]
                rs_type = x[1]
                up_size = x[5].replace("&nbsp;", " ")
                magnet = x[3]
                down_flag="0"
                up_datetime = format_datetime(x[4])

                # 单独处理hash_string，从magnet中提取
                dataReg = re.compile(r'''magnet:\?xt=urn:btih:(.+?)&amp;dn''')

                if len(dataReg.findall(magnet)) != 0:

                    hash_string = dataReg.findall(magnet)[0]
                    strSql = "select count(1) from get_tpb_all_magnet where hash_string = '%s' or rs_name = '%s';" % (hash_string, rs_name)
                    rtnCnt = mysqlExe.ExecQuery(strSql.encode('utf-8'))[0][0]

                    # 通过触发器取下一个计数号
                    totalNum = Get_SEQ_Next_Val("TPB_ALL_SEQ")

                    if rtnCnt < 1:

                        insertSQL="INSERT INTO get_tpb_all_magnet (up_datetime, hash_string, up_user, rs_name, rs_category, rs_type, up_size, magnet, down_flag) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (
                            up_datetime, hash_string, up_user, rs_name, rs_category, rs_type, up_size, magnet, down_flag
                        )

                        print (debug(), "%05d:%s:%02d:%02d 不存在，执行插入语句！%s，[ %s - %s ] : %s ! [ SQL ] : %s" % (
                                totalNum, singCategory, i, rnInPage, hash_string, rs_category, rs_type, rs_name, insertSQL
                            )
                        )
                        mysqlExe.ExecNonQuery(insertSQL.encode('utf-8'))
                    else:
                        print (debug(), "%05d:%s:%02d:%02d 已存在，跳过插入语句！%s，[ %s - %s ] : %s !" % (
                            totalNum, singCategory, i, rnInPage, hash_string, rs_category, rs_type, rs_name
                            )
                        )
                else:
                    print(debug(), "%05d:%s:%02d:%02d magnet 信息中没有包含 hash_string 规则的记录信息，跳过插入语句！%s，[ %s - %s ] : %s !" % (
                    totalNum, singCategory, i, rnInPage, hash_string, rs_category, rs_type, rs_name))


if __name__ == "__main__":


    try:

        # 清空计数器 方便从0开始计数
        Set_SEQ_Init_Val("TPB_ALL_SEQ");

        # 抓取TPB站的资源分类字典，不需要每次执行，如有变化执行一次
        # Get_TPB_Dict_2_DB_Dict(driver, siteWeb)

        allCategory = Get_DB_Dict("ALL")
        # allCategory = Get_DB_Dict("Porn")
        allCategory = random.sample(allCategory,len(allCategory)) # 随机打乱数组

        # for singCategory in allCategory:
        #     # poolParam = {"singCategory":singCategory,
        #     #              "siteWeb":siteWeb,
        #     #              "driver":driver
        #     #              }
        #     Down_TPB_Magent_Info(singCategory)

        # 设置多线程进程值
        p = Pool(5)
        for singCategory in allCategory:
            # poolParam = {"singCategory":singCategory,
            #              "siteWeb":siteWeb,
            #              "driver":driver
            #              }
            p.apply_async(Down_TPB_Magent_Info, args=(singCategory,))
        p.close()
        p.join()

    except Exception as e:
        print(e)
        traceback.print_exc()

    finally:

        driver.close()
        driver.quit()