# -*- coding:utf-8 -*-

import re, random, platform, os, sys, json, cookielib
from logger import *
import requests

req = requests.session()
req.cookies = cookielib.LWPCookieJar('cookies')
try:
    req.cookies.load(ignore_discard=True)
except:
    pass


def is_login():
    url = "https://www.zhihu.com/settings/profile"
    headers = {
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        'Accept-Encoding': "gzip, deflate, sdch, br",
        'Accept-Language': "en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4",
        'Host': "www.zhihu.com",
        'Connection': "keep-alive",
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"

    }
    r = req.get(url, allow_redirects=False, verify=False, headers=headers)
    status_code = int(r.status_code)
    if status_code == 301 or status_code == 302:
        return False
    elif status_code == 200:
        return True
    else:
        return None


def search_xsrf():
    url = "http://www.zhihu.com/"
    headers = {
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        'Accept-Encoding': "gzip, deflate, sdch",
        'Accept-Language': "en-US,en;q=0.8",
        'Host': "www.zhihu.com",
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"
    }
    r = req.get(url, verify=False, headers=headers)
    if int(r.status_code) != 200:
        raise network_error("request failed, response code: " + r.status_code)
    results = re.compile(r"\<input\stype=\"hidden\"\sname=\"_xsrf\"\svalue=\"(\S+)\"", re.DOTALL).findall(r.text)
    if len(results) < 1:
        return None
    return results[0]


def download_captcha():
    url = "https://www.zhihu.com/captcha.gif"
    headers = {
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        'Accept-Encoding': "gzip, deflate, sdch, br",
        'Accept-Language': "en-US,en;q=0.8",
        'Host': "www.zhihu.com",
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"
    }
    r = req.get(url, params={"r": random.random(), "type": "login"}, verify=False, headers=headers)
    if int(r.status_code) != 200:
        raise network_error("Failed to get CAPTCHA")
    image_name = u"verify." + r.headers['content-type'].split("/")[1]
    open(image_name, "wb").write(r.content)
    logger.info("Calling external application rendering CAPTCHA")
    if platform.system() == "Linux":
        logger.info(u"Command: xdg-open %s &" % image_name)
        os.system("xdg-open %s &" % image_name)
    elif platform.system() == "Darwin":
        logger.info(u"Command: open %s &" % image_name)
        os.system("open %s &" % image_name)
    elif platform.system() in ("SunOS,", "FreeBSD", "Unix", "OpenBSD", "NetBSD"):
        os.system("open %s $" % image_name)
    elif platform.system() == "Windows":
        os.system("%s" % image_name)
    else:
        logger.info("can't detect the OS, please type CAPTCHA manually")

    sys.stdout.write(termcolor.colored("Please enter CAPTCHA: ", "cyan"))
    captcha = raw_input()
    return captcha


def build_form(account, pwd):
    form = {"email": account, "password": pwd, "remember_me": True}
    form['_xsrf'] = search_xsrf()
    form['captcha'] = download_captcha()
    return form


def upload_form(form):
    url = "https://www.zhihu.com/login/email"
    headers = {
        'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
        'Host': "www.zhihu.com",
        'Origin': "http://www.zhihu.com",
        'Pragma': "no-cache",
        'Referer': "http://www.zhihu.com/",
        'X-Requested-With': "XMLHttpRequest"
    }
    r = req.post(url, data=form, headers=headers, verify=False)
    if int(r.status_code) != 200:
        raise network_error("Failed to request login form")
    if r.headers['content-type'].lower() == "application/json":
        try:
            result = json.loads(r.content)
        except Exception as e:
            logger.error("Failed to parse json")
            logger.debug(e)
            logger.debug(r.content)
            result = {}
        if result["r"] == 0:
            logger.success("Succeeded login")
            return {"result": True}
        elif result["r"] == 1:
            logger.error("Failed login")
            return {"error": {"code": int(result['errcode']), "message": result['msg'], "data": result['data']}}
        else:
            logger.warn(u"Unknown issue happened while uploading login form:    \n  \t  %s" % str(result))
            return {"error": {"code": -1, "message": u"unknown error"}}
    else:
        logger.warn("Couln't parse the response from server:   \n  \t  %s" % r.text)
        return {"error": {"code": -2, "message": u"parse error"}}


def login():
    if not is_login():
        account = "uniqueroysh@gmail.com"
        pwd = "whoami1985"

        form_data = build_form(account, pwd)

        result = upload_form(form_data)

        if "error" in result:
            if result["error"]['code'] == 1991829:
                # 验证码错误
                logger.error(u"验证码输入错误，请准备重新输入。")
                return login()
            elif result["error"]['code'] == 100005:
                # 密码错误
                logger.error(u"密码输入错误，请准备重新输入。")
                return login()
            else:
                logger.warn(u"unknown error.")
                return False
        elif "result" in result and result['result'] == True:
            logger.success("Success")
            req.cookies.save()
            return True


if __name__ == '__main__':
    login()
