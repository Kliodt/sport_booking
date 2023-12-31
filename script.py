import os
import time
from datetime import datetime
import re
import requests

# python3 script.py

#===========config=============
ids = [] #хранится в файле config.txt в строке ids:... от самого высокого приоритета к более низким (устанавл. в get_data_from_config_file())
token = "" #(хранится в файле token.txt)
r_token = "" #(хранится в файле token_refresh.txt)
tg_url = "https://api.telegram.org/bot6008414793:AAHNcOFOBtQ8Ney4C8GazYMh9zxtFzQuh2U/sendMessage?chat_id=-1001891587149&text={}" #отправлять смски в телегу

#==============================

def log(str):
    with open("log.log", "a+") as f:
        if len(str) < 1000:
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " ---- " + str.replace("\n", "") + "\n")
        else: #long error
            with open("long_error.log", "w+") as h:
                h.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " ---- \n" + str)
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " ---- (long error - записано в long_error.log) " + str[0:100] + ".....\n")


def set_patterns():
    global pattern2, pattern3, pattern4
    pattern2 = re.compile(fr"\"access_token\":([^,]*),") #access-token
    pattern3 = re.compile(fr"\"refresh_token\":([^,]*),") #refresh-token
    pattern4 = re.compile(r"\"available\"\:([0-9]+)\}") #parse line from log
    lf = open("log.log", "w+") #очистить логи
    le = open("long_error.log", "w+")
    le.close()
    lf.close()

def get_data_from_config_file():
    global ids
    with open("config.txt") as f:
        for line in f.readlines():
            if "ids:" in line:
                ids = eval(re.match(r"ids:\s*(\[.*\])", line, re.DOTALL).group(1))

def update_req_files():
    global token, r_token

    #получить токены из файлов
    with open("token.txt") as tok:
        token = tok.readline().replace("\n", "")
    with open("token_refresh.txt") as rtok:
        r_token = rtok.readline().replace("\n", "")

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
    with open("token_refresh.sh", "w") as rtok:
        for i in edited:
            rtok.write(i)
    log("значения обновлены: token, token_refresh, token in limits.sh")

def update_sign_in(id):
    #подставить айди и токен в файл sign_in
    with open("sign_in_for_lesson.sh") as sign_in:
        lines = sign_in.readlines()
        edited = [f"  --data-raw '[{id}]' \\\n" if "data-raw" in i else f"  -H 'authorization: Bearer {token}' \\\n" if "authorization" in i else i for i in lines]
    with open("sign_in_for_lesson.sh", "w") as sign_in:
        for i in edited:
            sign_in.write(i)

def update_sign_out(id):
    #подставить айди и токен в файл sign_out
    with open("sign_out_of_lesson.sh") as sign_out:
        lines = sign_out.readlines()
        edited = [f"  --data-raw '[{id}]' \\\n" if "data-raw" in i else f"  -H 'authorization: Bearer {token}' \\\n" if "authorization" in i else i for i in lines]
    with open("sign_out_of_lesson.sh", "w") as sign_out:
        for i in edited:
            sign_out.write(i)


def update_token():
    os.system("./token_refresh.sh > response.json 2> /dev/null")
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

def sign_in_for_lesson(id):
    update_sign_in(id)
    os.system("./sign_in_for_lesson.sh > response.json 2> /dev/null")
    with open("response.json", "r") as f:
        resp = f.readline()
    log("(попытка записи)" + resp)

    if "\"error_code\":0" in resp: #все ОК
        ids[ids.index(id)] *= -1
        send_message_for_me("успешно записан на: " + str(id))
        return True
    elif "\"error_code\":128" in resp:  #уже записан туда
        ids[ids.index(id)] *= -1
        send_message_for_me("уже был записан на: " + str(id))
        return True
    elif "\"error_code\":133" in resp:  #уже записан на 2 занятия в неделю
        current_priority = ids.index(id)
        log("уже записан на 2 занятия. Будет произведена попытка замены на более приоритетное")
        for i in range(len(ids)-1, -1, -1):
            if current_priority < i and ids[i] < 0: #то занятие на которое пытались записаться 
                #имеет больший приоритет (стоит в массиве раньше) 
                #и имеется (в списке) занятие i (получается с меньш приоритетом), откуда можно отписаться
                ids[i] = abs(ids[i])
                update_sign_out(ids[i])
                #отпис. от самого неприоритетного занятия, на которое записаны, чтоы записаться на более приоритетное
                os.system("./sign_out_of_lesson.sh > response.json 2> /dev/null")
                send_message_for_me("отписан от " + str(ids[i]))
                return sign_in_for_lesson(id)
        log("попытка замены провалилась")
    
    return False


def send_message_for_me(text):
    log("(Message) " + text)
    requests.get(tg_url.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " -- " + text))
        

#program
get_data_from_config_file()
set_patterns() #используют информацию из config.txt
update_req_files()
send_message_for_me("начало работы")
while len(ids) > 0:
    os.system("./limits.sh > response.json 2> /dev/null")
    with open("response.json", "r") as f:
        limits = f.readlines()
        limits = limits[0] if len(limits) != 0 else " "
    
    for id in ids:
        if id < 0: continue
        a = re.findall(fr"\"{id}\":[^,]*,[^,]*", limits)
        #------------обработка ошибок-------------
        if len(a)==0:
            log("(error)" + limits)
            if "\"error_code\":92" in limits:  #проблемы с токеном(30 мин)
                update_token()
                update_req_files()
                break  #exit "for"
            elif (not f"\"{str(id)}\"" in limits) and "\"error_code\":0" in limits: #такого номера нет в Limits новерное
                ids.remove(id)
                send_message_for_me("В limits нет такого id: " + str(id) + "; Id удален")
                break #exit for to update indexes in ids
            else:
                send_message_for_me("неизвестная ошибка")
        #------------------------------------------

        if len(a) > 0:
            log(a[0])
            available = re.search(pattern4, a[0])
            if available != None and int(available.group(1)) > 0:
                log("будет произведена попытка записи: ids==" + str(ids))
                if sign_in_for_lesson(id):
                    send_message_for_me("записан на: id==" + str(id))
                else:
                    log("не получилось записаться")
                log("осталось: ids==" + str(ids))
    #end of "for"      



    if (len(ids) == 1 and ids[0] < 0) or (len(ids) >= 2 and ids[0] < 0 and ids[1] < 0):
        send_message_for_me("записан на 2 занятия с наибольшим приоритетом")
        break #exit while and program

    time.sleep(3)



send_message_for_me("конец работы")