import re
import time
import json
import urllib.request
import http.client
import urllib.parse
import traceback
import paramiko

from Comm_Func import *
from Oper_Mysql_Class import *

def __Get_Session(hostDnsName,mgntPort,authStr):
    headers = {'Host': '%s:%s' % (hostDnsName,mgntPort) ,
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:28.0) Gecko/20100101 Firefox/28.0',
               'Accept': 'application/json, text/javascript, */*; q=0.01',
               'Connection': 'keep-alive',
               'Referer': 'http://%s:%s/transmission/web/' % (hostDnsName,mgntPort) ,
               'Authorization': 'Basic %s' % (authStr),
               'Origin': 'http://%s:%s' % (hostDnsName,mgntPort)
               }  # 虚拟主机头信息
    jdata={"":""}
    jdata=json.dumps(jdata)
    conn = http.client.HTTPConnection("%s" % hostDnsName,"%s" % mgntPort)
    conn.request('POST', '/transmission/rpc', jdata, headers)
    response = conn.getresponse()
    data = response.read().decode('utf-8')
    dataReg = re.compile(r'''<code>X-Transmission-Session-Id: (.+?)</code>''')
    rawDatas = dataReg.findall(data)
    conn.close()
    return rawDatas[0]

def __Delete_Transmission_Down_Task(ID,hostDnsName,mgntPort,authStr,tmSession,delFlag):

    headers = {'Host': '%s:%s' % (hostDnsName,mgntPort) ,
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:28.0) Gecko/20100101 Firefox/28.0',
               'Accept': 'application/json, text/javascript, */*; q=0.01',
               'Connection': 'keep-alive',
               'Referer': 'http://%s:%s/transmission/web/' % (hostDnsName,mgntPort) ,
               'Authorization': 'Basic %s' % (authStr),
               'Origin': 'http://%s:%s' % (hostDnsName,mgntPort),
               'X-Transmission-Session-Id':tmSession
               }

    # delete-local-data": true 删除 false 不删除
    jdata='{"method":"torrent-remove","arguments":{"ids":[%s],"delete-local-data":%s},"tag":""}' % (ID,delFlag)
    jdata=json.loads(jdata)
    jdata=json.dumps(jdata)
    conn = http.client.HTTPConnection("%s" % hostDnsName, "%s" % mgntPort)
    conn.request('POST', '/transmission/rpc', jdata, headers)
    response = conn.getresponse()
    data = response.read().decode('utf-8')
    data= json.loads(data)
    conn.close()

def __Get_Torrents_Info(hostDnsName,mgntPort,authStr,tmSession):

    headers = {'Host': '%s:%s' % (hostDnsName,mgntPort) ,
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:28.0) Gecko/20100101 Firefox/28.0',
               'Accept': 'application/json, text/javascript, */*; q=0.01',
               'Connection': 'keep-alive',
               'Referer': 'http://%s:%s/transmission/web/' % (hostDnsName,mgntPort) ,
               'Authorization': 'Basic %s' % (authStr),
               'Origin': 'http://%s:%s' % (hostDnsName,mgntPort),
               'X-Transmission-Session-Id':tmSession
               }

    jdata='{"method":"torrent-get","arguments":{"fields":["id","name","status","hashString","totalSize","percentDone","addedDate","trackerStats","leftUntilDone","rateDownload","rateUpload","recheckProgress","rateDownload","rateUpload","peersGettingFromUs","peersSendingToUs","uploadRatio","uploadedEver","downloadedEver","downloadDir","error","errorString"]},"tag":""}'
    jdata=json.loads(jdata)
    jdata=json.dumps(jdata)
    conn = http.client.HTTPConnection("%s" % hostDnsName,"%s" % mgntPort)
    conn.request('POST', '/transmission/rpc', jdata, headers)
    response = conn.getresponse()
    # print(response.status, response.reason)
    data = response.read().decode('utf-8')
    data= json.loads(data)
    # print(data)
    conn.close()

    arrTorrentsList={}
    listNum = 0

    for x in data["arguments"]["torrents"]:
        singTorrentsList={}
        singTorrentsList["ResourceName"] = x["name"]
        singTorrentsList["TotalSize"] = x["totalSize"]
        singTorrentsList["HashString"] = x["hashString"]
        singTorrentsList["PercentDone"] = x["percentDone"]
        singTorrentsList["DownEver"] = x["totalSize"] - x["leftUntilDone"]
        singTorrentsList["Status"] = x["status"]
        singTorrentsList["ID"] = x["id"]
        arrTorrentsList[listNum] = singTorrentsList
        listNum = listNum + 1

    return arrTorrentsList

def __Get_DB_New_Magnet(addTaskCnt):

    strSql = "SELECT up_datetime, up_user, rs_name, rs_category, rs_type, up_size, magnet, down_flag FROM get_tpb_all_magnet WHERE 0=0 "
    addstrSql2 = '''
        AND (rs_name LIKE 'Tokyo-Hot%'
        OR rs_name LIKE 'tokyo-Hot%'
        OR rs_name LIKE '%tokyo%hot%'
        OR rs_name LIKE '%Tokyo%hot%'
        OR rs_name LIKE '%1pondo%'
        OR rs_name LIKE 'tokyohot%') 
    '''
    strSql = strSql + addstrSql2

    sqlLimit = "ORDER BY up_datetime DESC LIMIT %s" % addTaskCnt

    extStrSql = "SELECT field_name, exoression, content FROM get_tpb_exten_condition WHERE table_name = 'get_tpb_all_magnet' and flag = '1';"
    rtnDatas = mysqlExe.ExecQuery(extStrSql.encode('utf-8'))

    addStrSql = ""
    for data in rtnDatas:
        addStrSql = addStrSql + "AND %s %s '%s' " % (data[0],data[1],data[2])

    strSql = strSql + addStrSql + sqlLimit

    rtnDatas = mysqlExe.ExecQuery(strSql.encode('utf-8'))
    # dataReg = re.compile(r'''btih:(.+?)&amp;dn=''')
    db_new_magnet = []
    for data in rtnDatas:
        db_new_magnet.append(data[6])
    return db_new_magnet

def __Add_Torrents_2_Transmission(dbNewMagnet, hostDnsName, mgntPort, authStr, downloadDir,tmSession):

    strNewMagnet = urllib.request.unquote(dbNewMagnet)

    headers = {'Host': '%s:%s' % (hostDnsName,mgntPort) ,
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:28.0) Gecko/20100101 Firefox/28.0',
               'Accept': 'application/json, text/javascript, */*; q=0.01',
               'Connection': 'keep-alive',
               'Referer': 'http://%s:%s/transmission/web/' % (hostDnsName,mgntPort) ,
               'Authorization': 'Basic %s' % (authStr),
               'Origin': 'http://%s:%s' % (hostDnsName,mgntPort),
               'X-Transmission-Session-Id':tmSession
               }

    jdata = '{"method":"torrent-add","arguments":{"filename":"%s","download-dir":"%s","paused":false},"tag":""}' % (strNewMagnet, downloadDir)
    # print(tmpinfo(),"jdata",jdata.replace('\t',' ').rstrip())
    jdata = jdata.replace('\t', ' ').rstrip() # 换掉tab键，否则json格式会报错
    jdata=json.loads(jdata)
    jdata=json.dumps(jdata)
    conn = http.client.HTTPConnection("%s" % hostDnsName, "%s" % mgntPort)
    conn.request('POST', '/transmission/rpc', jdata, headers)
    response = conn.getresponse()
    # print(tmpinfo(),response.status, response.reason)
    data = response.read().decode('utf-8')
    data= json.loads(data)
    # print(tmpinfo(),data)
    time.sleep(1)
    conn.close()
    return data

if __name__ == "__main__":

    try:
        print()

        print(debug(),"---------------------------------- 开始任务 --------------------------------------------------")

        # 获取 Transmission Session 信息
        paramInfo = Get_Param_In_DB("TM_INFO")
        hostDnsName = paramInfo["HOST_DNS_NAME"]
        mgntPort = paramInfo["HOST_PORT"]
        authStr = paramInfo["AUTH_STR"]
        tmSession = __Get_Session(hostDnsName,mgntPort,authStr)

        print()

        print (debug(),"获取 Transmission WEB Session 成功：%s" % tmSession)

        print()

        checkDate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        # 获取当前下载的种子信息 并返回重新组装后的字典列表
        torrInfoList = __Get_Torrents_Info(hostDnsName,mgntPort,authStr,tmSession)

        # 最终得出的实际下载总数应该为 realTaskCnt - delTaskCnt ，许要补充的数据记录数则为 MaxTaskCnt - realTaskCnt - delTaskCnt
        MaxTaskCnt = int(paramInfo["MAX_TASK_CNT"])  # 最大支持的下载任务记录
        delTaskCnt = 0 # 对已删除种子的计数，确认究竟删了多少条记录
        realTaskCnt = 0 # 当前实时任务数 任务状态包含 0 6 的

        for x in torrInfoList:
            # print(debug(),torrInfoList[x])

            resourceName = torrInfoList[x]["ResourceName"]
            resourceName = resourceName.replace("'", "''")
            totalSize = torrInfoList[x]["TotalSize"]
            hashString = torrInfoList[x]["HashString"]
            percentDone = torrInfoList[x]["PercentDone"]
            downEver = torrInfoList[x]["DownEver"]
            taskStatus = torrInfoList[x]["Status"]
            ID = torrInfoList[x]["ID"]

            strSql = "SELECT hash_string, resource_name, percent_done, down_flag FROM check_transm_down WHERE hash_string = '%s';" % hashString

            rtnDatas = mysqlExe.ExecQuery(strSql.encode('utf-8'))

            # 如果没有返回值，则认为是一条新增记录
            if len(rtnDatas) == 0 :
                strSql="INSERT INTO check_transm_down (resource_name, total_size, hash_string, percent_done, down_ever, check_date) VALUES ('%s', '%s', '%s', '%s', '%s', '%s');" % (
                    resourceName, totalSize, hashString, percentDone, downEver, checkDate
                )
                print(debug(),"新增下载任务到统计表：%s" % strSql)
                mysqlExe.ExecNonQuery(strSql.encode('utf-8'))

                # 该赋值用于后续判断
                dbResourceName = ""
                dbDownFlag = "0"

            else:
                dbResourceName = rtnDatas[0][1]
                dbDownFlag = rtnDatas[0][2]

            # 判断已存在记录，多种情况

            if taskStatus == 0 or taskStatus == 6 :

                if int(dbDownFlag) == 1 :
                    print(debug(),"无需操作完成的任务：hash_string = '%s',dbResourceName = '%s' 的下载任务已完成归档，无需再次操作！" % (hashString, dbResourceName))
                else:
                    strSql = "UPDATE check_transm_down SET resource_name='%s', percent_done='%s', down_ever='%s', check_date='%s', down_flag='1' WHERE hash_string='%s' and down_flag<>'1';" % (
                        resourceName, percentDone, downEver, checkDate, hashString
                    )
                    print(debug(),"更新完成的下载链接：%s" % strSql)
                    mysqlExe.ExecNonQuery(strSql.encode('utf-8'))
                if taskStatus == 0:
                    __Delete_Transmission_Down_Task(ID, hostDnsName, mgntPort, authStr, tmSession, "false")
                    time.sleep(2)
                    print(debug(), "清理已经完结的任务：hash_string = '%s' 的资源已完成下载，且非上传状态，将自动从下载列表中清除！" % (hashString))
            else:

                # 除去上述状态 其他种子状态均需做累加
                realTaskCnt = realTaskCnt + 1

                if taskStatus == 3 :
                    strSql = "UPDATE check_transm_down SET resource_name='%s', percent_done='%s', down_ever='%s', check_date='%s' WHERE  hash_string='%s';" % (
                                resourceName, percentDone, downEver, checkDate, hashString
                            )
                    print(debug(),"等待下载的任务更新：%s" % strSql)
                    mysqlExe.ExecNonQuery(strSql.encode('utf-8'))

                elif taskStatus == 4 :

                    strSql = "SELECT a.down_ever,a.check_date FROM check_transm_down a WHERE a.hash_string = '%s';" % hashString
                    rtnDatas = mysqlExe.ExecQuery(strSql.encode('utf-8'))
                    dbDownEver = int(rtnDatas[0][0])
                    dbCheckDate = rtnDatas[0][1]
                    formatCheckDate = datetime.datetime.strptime(checkDate, "%Y-%m-%d %H:%M:%S")

                    diffDays = (formatCheckDate - dbCheckDate).days

                    if diffDays > 1 and dbDownEver == downEver :

                        print(debug(),"清理停止的下载任务：HashString = '%s' 的资源超过 %s 天没有任何进度，将自动从下载列表中清除！" % (hashString, diffDays))

                        strSql = "UPDATE check_transm_down SET down_flag = '9' WHERE hash_string = '%s';" % hashString
                        mysqlExe.ExecNonQuery(strSql.encode('utf-8'))

                        # 删除操作
                        __Delete_Transmission_Down_Task(ID,hostDnsName,mgntPort,authStr,tmSession, "true")

                        # 每删除一个过期任务，需要累计加1 后面计算满100任务的时候可以冲抵差异
                        delTaskCnt = delTaskCnt + 1

                    elif  diffDays <=3 and dbDownEver != downEver:

                        strSql = "UPDATE check_transm_down SET resource_name='%s', percent_done='%s', down_ever='%s', check_date='%s' WHERE  hash_string='%s';" % (
                            resourceName, percentDone, downEver, checkDate, hashString
                        )
                        print(debug(),"运行中任务进度更新：%s" % strSql)
                        mysqlExe.ExecNonQuery(strSql.encode('utf-8'))

        print()
        addTaskCnt = MaxTaskCnt - realTaskCnt + delTaskCnt # 任务总数 = 最大保持的数量 减去现在正运行的数量 再加上 运行中被删除的静止任务 就是需要补充的下载任务
        if addTaskCnt <= 0 :
            print(debug(),"目前预设的任务总数为：%s, 已存在正在执行或等待执行的任务总数为：%s，目前无需新增任何新下载任务！" %  (MaxTaskCnt, realTaskCnt))
        else:
            print(debug(),"目前预设的任务总数为：%s, 已存在正在执行或等待执行的任务总数为：%s，需新增：%s 条记录！" %  (MaxTaskCnt, realTaskCnt - delTaskCnt, addTaskCnt))

            dbNewMagnetList = __Get_DB_New_Magnet(addTaskCnt)
            todayYYYYMMDD = datetime.datetime.now().strftime("%Y%m%d")
            # downloadDir = "/share/CACHEDEV1_DATA/Datas/Bad_Item/transmission/downloads/%s" % todayYYYYMMDD
            downloadDir = "/share/CACHEDEV1_DATA/Datas/Bad_Item/transmission/downloads"

            for dbNewMagnet in dbNewMagnetList:

                dbNewMagnet = dbNewMagnet.decode('utf-8') # blob字段转str

                rtnDatas = __Add_Torrents_2_Transmission(dbNewMagnet, hostDnsName, mgntPort, authStr, downloadDir,tmSession)

                if rtnDatas["result"] == "success":

                    strSql = "UPDATE get_tpb_all_magnet SET down_flag='1' WHERE hash_string = '%s';" % rtnDatas["arguments"]["torrent-added"]["hashString"]
                    print(debug(), "修改已 POST 的种子信息：%s" % strSql)
                    mysqlExe.ExecNonQuery(strSql.encode('utf-8'))

                    strSql = "INSERT INTO check_transm_down (resource_name, total_size, hash_string, percent_done, down_ever, check_date) VALUES ('%s', '%s', '%s', '%s', '%s', '%s');" % (
                        rtnDatas["arguments"]["torrent-added"]["hashString"], 0, rtnDatas["arguments"]["torrent-added"]["hashString"], 0, 0, checkDate
                    )
                    print(debug(), "新增下载任务到统计表：%s" % strSql)
                    mysqlExe.ExecNonQuery(strSql.encode('utf-8'))

        # print("\n-----------------------------------开始同步任务-----------------------------------------------")
        # _ssh_sync_files()

    except Exception as e:
        traceback.print_exc()
        print(e)
