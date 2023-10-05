import os
import time
from datetime import datetime
import re
import requests

# python3 script.py

#===========config=============
id = 0 #хранится в файле config.txt в строке id:....
token = "" #(хранится в файле token.txt)
r_token = "" #(хранится в файле token_refresh.txt)
tg_url = "https://api.telegram.org/bot6008414793:AAHNcOFOBtQ8Ney4C8GazYMh9zxtFzQuh2U/sendMessage?chat_id=-1001891587149&text={}" #отправлять смски в телегу

#==============================

def log(str):
    with open("log.log", "a+") as f:
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " ---- " + str + "\n")

def set_patterns():
    global pattern, pattern2, pattern3, pattern4
    pattern = re.compile(fr"\"{id}\":[^,]*,[^,]*") #кусок json-а с нужным занятием
    pattern2 = re.compile(fr"\"access_token\":([^,]*),") #access-token
    pattern3 = re.compile(fr"\"refresh_token\":([^,]*),") #refresh-token
    pattern4 = re.compile(r"\"available\"\:([0-9]+)\}") #parse line from log
    lf = open("log.log", "w+") #очистить лог
    lf.close()

def get_data_from_config_file():
    global id
    with open("config.txt") as f:
        for line in f.readlines():
            if "id:" in line:
                id = int(re.match(r"id:\s*([0-9]*)", line, re.DOTALL).group(1))

def update_req_files():
    #получить токены из файлов
    with open("token.txt") as tok:
        token = tok.readline().replace("\n", "")
    with open("token_refresh.txt") as rtok:
        r_token = rtok.readline().replace("\n", "")

    #подставить айди и токен в файл sign_in
    with open("sign_in_for_lesson.sh") as sign_in:
        lines = sign_in.readlines()
        edited = [f"  --data-raw '[{id}]' \\\n" if "data-raw" in i else f"  -H 'authorization: Bearer {token}' \\\n" if "authorization" in i else i for i in lines]
    with open("sign_in_for_lesson.sh", "w") as sign_in:
        for i in edited:
            sign_in.write(i)

    #подставить токен в limits
    with open("limits.sh") as lims: 
        lines = lims.readlines()
        edited = [f"  -H 'authorization: Bearer {token}' \\\n" if "authorization" in i else i for i in lines]
    with open("limits.sh", "w") as lims:
        for i in edited:
            lims.write(i)

    #подставить r-токен в token_refresh
    with open("token_refresh.sh") as rtok:
        lines = rtok.readlines()
        edited = [f"  --data-raw 'refresh_token={r_token}&scopes=openid%20profile&client_id=student-personal-cabinet&grant_type=refresh_token' \\\n" if "--data-raw" in i else i for i in lines]

    log("значения обновлены")


def update_token():
    os.system("./token_refresh.sh > response.json")
    with open("response.json", "r") as f:
        resp = f.readlines()
        for i in resp:
            access = re.findall(pattern2, i)
            refre = re.findall(pattern3, i)
            if len(access) > 0:
                with open("token.txt", "w") as f:
                    f.write(access[0].replace(" ", "").replace("\"", ""))
            if len(refre) > 0:
                with open("token_refresh.txt", "w") as f:
                    f.write(refre[0].replace(" ", "").replace("\"", ""))
    log("токены обновлены и записаны в файлы")

def sign_in_for_lesson():
    os.system("./sign_in_for_lesson.sh > response.json")
    with open("response.json", "r") as f:
        resp = f.readline()
        log("(попытка записи)" + resp)
        if "\"error_code\":0" in resp:
            return True
    return False

def send_message_for_me(text):
    requests.get(tg_url.format(text))
        

#program
get_data_from_config_file()
set_patterns() #используют информацию из config.txt
update_req_files()
while True:
    os.system("./limits.sh > response.json")
    with open("response.json", "r") as f:
        limits = f.readlines()[0]
    a = re.findall(pattern, limits)
    #------------обработка ошибок-------------
    if len(a)==0:
        log("(error)" + limits)
        if "\"error_code\":92" in limits:  #проблемы с токеном(30 мин)
            update_token()
            update_req_files()
            continue
        else:
            log("неизвестная ошибка")
            send_message_for_me("неизвестная ошибка")
    #------------------------------------------

    if len(a) > 0:
        log(a[0])
        available = re.search(pattern4, a[0])
        if available != None and int(available.group(1)) > 0:
            if sign_in_for_lesson():
                log("записан")
                send_message_for_me("записан на " + str(id))
                break
            else:
                log("не получилось")
            

    time.sleep(3)


