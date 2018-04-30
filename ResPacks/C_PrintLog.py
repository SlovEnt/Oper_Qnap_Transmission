# -*- coding: utf-8 -*-
__author__ = 'SlovEnt'
__date__ = '2018/4/28 21:26'

from datetime import datetime
import time
import sys

class C_PrintLog(object):
    def __init__(self, logFile=""):
        self.logFile = logFile

    def wp_debug(self, msg=""):
        now = datetime.datetime.now()
        print("\033[1;34mDEBUG INFO: " + now.strftime("%Y-%m-%d %H:%M:%S") + ":\033[0m", msg)
        self.logFile.write(now.strftime("%Y-%m-%d %H:%M:%S") + ": " + msg + "\n")

    def wp_error(self, msg=""):
        now = datetime.datetime.now()
        print("\033[1;31mERROR INFO: " + now.strftime("%Y-%m-%d %H:%M:%S") + ":\033[0m", msg)
        self.logFile.write(now.strftime("%Y-%m-%d %H:%M:%S") + ": " + msg + "\n")

    def wp_warning(self, msg=""):
        now = datetime.datetime.now()
        print("\033[1;31mWarning INFO: " + now.strftime("%Y-%m-%d %H:%M:%S") + ":\033[0m", msg)
        self.logFile.write(now.strftime("%Y-%m-%d %H:%M:%S") + ": " + msg + "\n")

    def debug(msg=""):
        now = datetime.datetime.now()
        print("\033[1;34mDEBUG INFO: " + now.strftime("%Y-%m-%d %H:%M:%S") + ":\033[0m", msg)

    def errinfo(msg=""):
        now = datetime.datetime.now()
        print("\033[1;31mERROR INFO: " + now.strftime("%Y-%m-%d %H:%M:%S") + ":\033[0m", msg)

    def tmpinfo(msg=""):
        now = datetime.datetime.now()
        # if msg != "":
        #     msg = " " + msg
        print("\033[1;32mTEMP INFO: " + now.strftime("%Y-%m-%d %H:%M:%S") + ":\033[0m", msg)

    def Time_Remain(msg, showMins):
        now = datetime.datetime.now()
        cnt = 0
        while (cnt < showMins):
            cnt += 1
            n = showMins - cnt
            time.sleep(1)
            sys.stdout.write("\r" + "\033[1;34mDEBUG INFO: " + now.strftime("%Y-%m-%d %H:%M:%S") + ":\033[0m " +  msg %(n) , )
            if  cnt == showMins:
                sys.stdout.write("\n")
            sys.stdout.flush()
            if not n:
                return "完成"
