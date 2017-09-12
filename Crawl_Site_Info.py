
import re
import datetime

from Comm_Func import *
from Oper_Mysql_Class import MySQL, mysqlExe
import urllib.request

if __name__ == "__main__":

    enterHttpUrl = "https://proxybay.one/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    req = urllib.request.Request(url=enterHttpUrl, headers=headers)
    pageSourceScript = urllib.request.urlopen(req).read()

    pageSourceScript = pageSourceScript.decode('UTF-8')
    # print(pageSourceScript)
    dataReg = re.compile(r'''<tr><td class="site"><a rel="nofollow" class="t1" href="(.+?)">.+?</a></td><td class="country"><img src="assets/img/flags/.+?.gif" alt=".+?" title="(.+?)"></td><td class="status"><img alt=".+?" src="assets/img/(.+?).png"></td><td class="speed">(.+?)</td></tr>''')
    rawDatas = dataReg.findall(pageSourceScript)
    # print (rawDatas)

    for x in rawDatas:
        sqlstr = "select count(1) from crawling_site_info where site = '" + x[0] + "';"
        listsql = mysqlExe.ExecQuery(sqlstr.encode('utf-8'))
        cnt = int(listsql[0][0])

        if cnt <1 :
            insertSQL = "INSERT INTO crawling_site_info (site, country, status, speed) VALUES ('"+x[0]+"', '"+x[1]+"', '"+x[2]+"', '"+x[3]+"');"
        else:
            insertSQL = "UPDATE crawling_site_info SET site='"+x[0]+"', country='"+x[1]+"', status='"+x[2]+"', speed='"+x[3]+"' WHERE site='"+x[0]+"';"
        mysqlExe.ExecNonQuery(insertSQL.encode('utf-8'))
        print (insertSQL)

    enterHttpUrl = "http://144.217.84.47/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    req = urllib.request.Request(url=enterHttpUrl, headers=headers)
    pageSourceScript = urllib.request.urlopen(req).read()

    pageSourceScript = pageSourceScript.decode('UTF-8')
    # print(pageSourceScript)
    dataReg = re.compile(r'''<input type="button" value="  (.+?) " onclick="window.location='(.+?)'">''')
    dataReg = re.compile(r'''rel="nofollow">(.+?)</a><br>''')

    rawDatas = dataReg.findall(pageSourceScript)
    # print (rawDatas)

    for x in rawDatas:

        sqlstr = "select count(1) from crawling_site_info where site = '" + x + "';"
        listsql = mysqlExe.ExecQuery(sqlstr.encode('utf-8'))
        cnt = int(listsql[0][0])

        if cnt < 1:
            insertSQL = "INSERT INTO crawling_site_info (site, country, status, speed) VALUES ('%s','','','');" % (x)
        else:
            insertSQL = "UPDATE crawling_site_info SET site='" + x + "', country='" + "" + "' WHERE site='" + x + "';"
        mysqlExe.ExecNonQuery(insertSQL.encode('utf-8'))
        print(insertSQL)
