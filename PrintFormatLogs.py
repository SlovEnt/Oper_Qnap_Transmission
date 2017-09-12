import datetime

def debug():
    now = datetime.datetime.now()
    return "\033[1;34mDEBUG INFO: " + now.strftime("%Y-%m-%d %H:%M:%S")+":\033[0m"

def errinfo():
    now = datetime.datetime.now()
    return "\033[1;31mERROR INFO: " + now.strftime("%Y-%m-%d %H:%M:%S")+":\033[0m"

def tmpinfo(msg=""):
    now = datetime.datetime.now()
    if msg != "":
        msg = " " + msg
    return "\033[1;32mTEMP INFO: " + now.strftime("%Y-%m-%d %H:%M:%S") + msg + ":\033[0m"

# print(tmpinfo(),"swerwrwe")
