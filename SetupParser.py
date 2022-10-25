# -*- coding:utf-8 -*-
from configparser import ConfigParser


def read_setup():
    # 以字典的方式读取配置对象中的数据
    config = ConfigParser()
    config.read("setup.ini", encoding='utf-8')

    print(config.sections())
    dic = {}
    web_browser = config["DEFAULT"]["WebBrowser"]
    dic["WebBrowser"] = web_browser
    dic["WebDriver"] = config["WebDriver"][web_browser]
    dic["JD_website"] = config["JD"]["website"]

    try:
        username = config["DEFAULT"]["username"]
        password = config["DEFAULT"]["password"]
        dic["username"] = username
        dic["password"] = password
    except(TypeError, ValueError):
        print("No default account")

    return dic
