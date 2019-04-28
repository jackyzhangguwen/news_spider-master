#_*_encoding:utf-8_*_


# 网络请求库
import requests

# 日期时间库
import time

# 正则表达式库
import re

# 异常堆栈
import traceback

# 系统核心
import os

# 虎嗅网
from spider.huxiu import huxiu

# 钛媒体
from spider.tmtpost import tmtpost

# 早读课
from spider.zaodu import zaodu

# 产品100
from spider.chanpin import chanpin

# 产品中国
from spider.pmtoo import pmtoo

# 人人都是产品经理
from spider.woshipm import woshipm

# 雷锋网
from spider.leiphone import leiphone

# 36氪
from spider.kr import kr

# 文件写入
from Write_File import write

# Mysql写入
from Write_Db import writeIntoMysql

from Write_Db import is_url_processed

from Write_Log import writelog

import pymysql

import configparser

# json库
import json

import sys

class program(object):
    def __init__(self):
        self.headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate", "Accept-Language": "zh-CN,zh;q=0.8", "Cache-Control": "max-age=0",
        "Connection": "keep-alive", "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36", }


    # 获取当前系统的时间，类型为：str
    def time_now(self):
        time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        return time_now

    def main(self):
        print(self.time_now(),'\t程序启动中，请等待......\n')
        hour_counter = 1

        # 打开数据库连接
        cfg = configparser.ConfigParser()
        cfg.read("conf.ini")
        db_host = cfg.get("database", "host")
        db_port = cfg.getint("database", "port")
        db_name = cfg.get("database", "dbname")
        db_user = cfg.get("database", "user")
        db_pass = cfg.get("database", "pass")
        pref_write_file = cfg.getint("preference", "writefile")

        while(True):
            print(self.time_now(), '\t-------- 开始处理第{}次调度! --------\n'.format(hour_counter))

            db = pymysql.connect(host=db_host, user=db_user, password=db_pass,db=db_name,port=db_port, use_unicode=True, charset="utf8")
            cur = db.cursor()
            sql_select_from_web_src = "select id,name,platform_id,url,img from 91_web_src"
            cur.execute(sql_select_from_web_src)
            result_data = cur.fetchall()
            for id,name,platform_id,url,img in result_data:
                print(" 从91_web_src表中查询到记录：", id, name, platform_id, url)
                print("\n 处理中，详情请查看log文件......\n")
                if url.startswith("https://www.huxiu.com"):
                    hu = huxiu()
                    inner_url_list = hu.get_inner_url_list_new(url)
                    for inner_url in inner_url_list:
                        if is_url_processed(inner_url['link']) == True:
                            continue
                        news = hu.get_news(url = inner_url['link'])
                        if pref_write_file == 1:
                            write(news)
                        writeIntoMysql(news, id, name, platform_id, inner_url['img'], inner_url['desc'])
                elif url.startswith("https://36kr.com"):
                    kr36 = kr ()
                    inner_url_list = kr36.get_inner_url_list_new(url)
                    for inner_url in inner_url_list:
                        if is_url_processed(inner_url['link']) == True:
                            continue
                        news = kr36.get_news(url = inner_url['link'], title = inner_url['title'], summary = inner_url['desc'])
                        if pref_write_file == 1:
                            write(news)
                        writeIntoMysql(news, id, name, platform_id, inner_url['img'], inner_url['desc'])
                elif url.startswith("http://36kr.com"):
                    kr36 = kr ()
                    inner_url_list = kr36.get_inner_url_list_new(url)
                    for inner_url in inner_url_list:
                        if is_url_processed(inner_url['link']) == True:
                            continue
                        news = kr36.get_news(url = inner_url['link'], title = inner_url['title'], summary = inner_url['desc'])
                        if pref_write_file == 1:
                            write(news)
                        writeIntoMysql(news, id, name, platform_id, inner_url['img'], inner_url['desc'])

            cur.close()
            db.close()

            print(self.time_now(), '\t======== 第{}次调度处理结束! ========\n'.format(hour_counter))

            # 两小时扫描一次数据库
            time.sleep(7200)
            hour_counter += 1

if __name__ == '__main__':
    # 全局异常捕获
    # 定义全局异常处理器
    def _excepthook(type, value, trace):

        print(self.time_now(), "捕获到全局异常，类型:{}，值:{}\n".format(str(type), str(value)))
        print(self.time_now(), "按任意键继续")
        os.system('pause')

        err_msg = '\n ======================== 捕获到全局异常 ======================== \n'
        err_msg += ''.join(traceback.format_exception(type, value, trace))
        writelog(err_msg)

        sys.__excepthook__(type, value, trace)

    sys.excepthook = _excepthook

    program = program()
    program.main()
