#!usr/bin/env python
# -*- coding: utf-8 -*-

from math import ceil
from time import strftime
from random import uniform
from requests import Session
from bs4 import BeautifulSoup
from sys import argv


RSA_E = "010001"
RSA_M = \
    "008aed7e057fe8f14c73550b0e6467b023616ddc8fa91846d2613cdb7f7621e3cada4cd5d812d627af6b87727ade4e26d26208b7326815941492b2204c3167ab2d53df1e3a2c9153bdb7c8c2e968df97a5e7e01cc410f92c4c2c2fba529b3ee988ebc1fca99ff5119e036d732c368acf8beba01aa2fdafa45b21e4de4928d0d403"


def print_log(string):
    print(strftime("%Y-%m-%d %H:%M:%S") + "\t" + string)

def get_rsa_password(password, e, m):
    # Reference: https://www.cnblogs.com/himax/p/python_rsa_no_padding.html
    m = int.from_bytes(bytearray.fromhex(m), byteorder='big')
    e = int.from_bytes(bytearray.fromhex(e), byteorder='big')
    plain_text = password[::-1].encode("utf-8")
    input_nr = int.from_bytes(plain_text, byteorder='big')
    crypted_nr = pow(input_nr, e, m)
    key_length = ceil(m.bit_length() / 8)
    crypted_data = crypted_nr.to_bytes(key_length, byteorder='big')
    
    return crypted_data.hex()

def login_sues_cas_success_or_not(username, password, session):
    result = session.get("https://cas.sues.edu.cn/cas/login")
    soup = BeautifulSoup(result.content, "lxml")
    execution = soup.find("input", {"name": "execution"}).attrs["value"]
    data = {
        "username": username, "password": get_rsa_password(password, RSA_E, RSA_M), "execution": execution,
        "encrypted": "true", "_eventId": "submit", "loginType": "1", "submit": "登 录"
    }
    result = session.post("https://cas.sues.edu.cn/cas/login", data)
    soup = BeautifulSoup(result.content, "lxml")
    
    if soup.find("div", {"class": "success"}):
        return True
    else:
        return False

def report(person):
    username = person["CASUsername"]
    password = person["CASPassword"]
    session = Session()
    session.headers.update({
        "Accept":
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,"
            "application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding":
            "gzip, deflate",
        "Accept-Language":
            "zh-CN,zh;q=0.9",
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 "
            "Safari/537.36 Edg/87.0.664.75"
    })
    flag = login_sues_cas_success_or_not(username, password, session)
    
    if not flag:
        return False, "Fail to Login! "
    
    url1 = "https://cas.sues.edu.cn/cas/login?service=https%3A%2F%2Fworkflow.sues.edu.cn%2Fdefault%2Fwork%2Fshgcd" \
           "%2Fjkxxcj%2Fjkxxcj.jsp"
    result = session.get(url1)
    new_header = {
        "Accept": "*/*", "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6", "Content-Type": "text/json",
        "Origin": "https://workflow.sues.edu.cn",
        "Referer": "https://workflow.sues.edu.cn/default/work/shgcd/jkxxcj/jkxxcj.jsp", "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin", "X-Requested-With": "XMLHttpRequest"
    }
    session.headers.update(new_header)
    
    if (int(strftime("%H")) + 8) % 24 < 12:  # GitHub Action: UTC(+0), Transform to UTC(+8)
        period = "上午"
    else:
        period = "下午"
    
    # if int(strftime("%H")) < 12:
    #     period = "上午"
    # else:
    #     period = "下午"
    
    date = strftime("%Y-%m-%d")
    now = strftime("%Y-%m-%d %H:%M")
    
    '''
    You Can Fill in Past or Future Dates here. For Example:
    period = "下午"
    date = "2021-01-28 15:00"
    '''
    
    first_request_json = {
        "params": {"empcode": username}, "querySqlId": "com.sudytech.work.shgcd.jkxxcj.jkxxcj.queryEmp"
    }
    second_request_json = {
        "params": {"empcode": username}, "querySqlId": "com.sudytech.work.shgcd.jkxxcj.jkxxcj.queryNear"
    }
    first_result = session.post(
        "https://workflow.sues.edu.cn/default/work/shgcd/jkxxcj/com.sudytech.portalone.base.db"
        ".queryBySqlWithoutPagecond.biz.ext",
        json=first_request_json)
    second_result = session.post(
        "https://workflow.sues.edu.cn/default/work/shgcd/jkxxcj/com.sudytech.portalone.base.db"
        ".queryBySqlWithoutPagecond.biz.ext",
        json=second_request_json)
    
    if len(second_result.json()["list"]) == 0:
        return False, "Fail to Get Last Report! "
    
    person = second_result.json()["list"][0]
    update_data = {
        "params": {
            "id": person["ID"], "sqrid": person["SQRID"], "sqbmid": person["SQBMID"], "rysf": person["RYSF"],
            "sqrmc": person["SQRMC"], "gh": person["GH"], "sfzh": person["SFZH"], "sqbmmc": person["SQBMMC"],
            "xb": person["XB"], "lxdh": person["LXDH"], "nl": person["NL"], "tjsj": now, "xrywz": person["XRYWZ"],
            "sheng": person["SHENG"], "shi": person["SHI"], "qu": person["QU"], "jtdzinput": person["JTDZINPUT"],
            "gj": "", "jtgj": "", "jkzk": person["JKZK"], "jkqk": person["JKQK"],
            "tw": str(round(uniform(36.3, 36.8), 1)), "sd": period, "bz": "", "_ext": "{}"
        }
    }
    print_log(update_data["params"]["gh"] + "\t" + update_data["params"]["tw"])
    url2 = "https://workflow.sues.edu.cn/default/work/shgcd/jkxxcj/com.sudytech.work.shgcd.jkxxcj.jkxxcj.saveOrUpdate" \
           ".biz.ext"
    final_result = session.post(url2, json=update_data)
    
    if final_result.json()['result']["success"]:
        return True, None
    else:
        return False, "[" + final_result.json()['result']['errorcode'] + "]" + final_result.json()['result']['msg']


if __name__ == '__main__':
    person = {"CASUsername": argv[1], "CASPassword": argv[2]}
    session = Session()
    session.headers.update({
        "Accept":
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,"
            "application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding":
            "gzip, deflate",
        "Accept-Language":
            "zh-CN,zh;q=0.9",
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 "
            "Safari/537.36 Edg/87.0.664.75"
    })
    result = login_sues_cas_success_or_not(person["CASUsername"], person["CASPassword"], session)
    
    if result:
        print_log("Login SUES CAS Successful! ")
    else:
        print_log("Fail to Login SUES CAS! ")
        quit()
    
    state, message = report(person)
    
    if state:
        print_log("Report Successful! ")
    else:
        print_log("Fail to Report! \t" + message)
