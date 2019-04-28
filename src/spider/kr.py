#_*_encoding:utf-8_*_

from selenium import webdriver

from selenium.common.exceptions import NoSuchElementException

import urllib.request

import urllib.parse

import ssl

import time

import sys, traceback

import requests

import json

import re

sys.path.append("..")
from Write_Log import writelog


class kr(object):

    def __init__(self):
        self.base_url = 'https://36kr.com/'

    # 初始化phantomjs，并设置窗口大小，默认300 X 400，返回移动端页面
    def create_phantomJS(self):
        # # selenium新版本已放弃对phantomjs的支持，以下改用chrome无界面模式
        driver = webdriver.PhantomJS(executable_path="C:/Program Files/phantomjs-2.1.1-windows/bin/phantomjs.exe")
        driver.set_window_size(1024, 768)

        # # 创建chrome参数对象
        # opt = webdriver.ChromeOptions()

        # # 把chrome设置成无界面模式，不论windows还是linux都可以，自动适配对应参数
        # opt

        # # 创建chrome无界面对象
        # driver = webdriver.Chrome(options=opt)

        return driver

    def get_html_encode(self, content_type, page_raw):
        '''
        : param content_type : str, response header的参数 一般有编码方式
        : param page_raw : str, html源码信息，里面的meta里面一般有编码方式
        : return : 返回编码方式
        '''
        encode_list = re.findall(
            r'charset=([0-9a-zA-Z_-]+)', content_type, re.I
        )
        if encode_list:
            return encode_list[0]
        encode_list = re.findall(
            r'<meta.+charset=[\'"]*([0-9a-zA-Z_-]+)', page_raw, re.I
        )
        if encode_list:
            return encode_list[0]

    def _get_craw(self, url, headers, get_payload):
        '''
        : param url:str,Request URL
        : param headers: dict,Request Headers
        : param get_payload: dict,Query String Parameters
        : return:
        '''
        r = requests.get(url, headers=headers, params=get_payload)
        if r.status_code != 200:
            raise Exception(r.status_code)
        content_type = r.headers['Content-Type']
        if 'text/html' in content_type:
            encoding = self.get_html_encode(content_type, r.text)
            if encoding:
                r.encoding = encoding
            return r.text
        elif 'application/json' in content_type:
            return r.text
        elif 'application/pdf' in content_type:
            return r.content    # 返回字节
        elif 'image' in content_type:# 图片
            return r.content    # 返回字节
        else:
            return r.content

    def _post_craw(self, url, headers, get_payload):
        '''
        : param url:str,Request URL
        : param headers: dict,Request Headers
        : param get_payload: dict,Query String Parameters
        : return:
        '''
        r = requests.post(url, headers=headers, params=get_payload)
        if r.status_code != 200:
            raise Exception(r.status_code)
        content_type = r.headers['Content-Type']
        if 'text/html' in content_type:
            encoding = get_html_encode(content_type, r.text)
            if encoding:
                r.encoding = encoding
            return r.text
        elif 'application/json' in content_type:
            return r.text
        elif 'application/pdf' in content_type:
            return r.content    # 返回字节
        elif 'image' in content_type:# 图片
            return r.content    # 返回字节
        else:
            return r.content

    def _craw(self, method, url, headers=None, payload=None):
        try:
            if method == 'get':
                return self._get_craw(url, headers, payload)
            elif method == 'post':
                return self._post_craw(url, headers, payload)
            else:
                raise Exception('method is wrong')
        except Exception as e:
            print(url)
            print(e)

    def get_inner_url_list_new(self, url):
        writelog("====>>>> 36kr开始解析原始URL:{}\n".format(url))
        inner_url_list = []
        get_payload = {
            'per_page':20,
            'page':1,
            '_':str(int(time.time() * 1000))
        }
        headers = {
            'Host':'36kr.com',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        }
        data = self._craw('get', url, headers, get_payload)

        data = json.loads(data)
        articles = data['data']['items']
        for article in articles:
            # 每条资讯对应一个字典
            item = {}
            item['title'] = article['title']
            item['link'] = 'https://36kr.com/p/{}.html'.format(article['id'])
            item['desc'] = article['summary']
            item['img'] =  article['cover']
            inner_url_list.append(item)

        # writelog("36kr返回inner_url_list内容如下:\n" + json.dumps(inner_url_list) + "\n")

        return inner_url_list

    # 获取网页源码
    def getHtml(self, url):
        header = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:48.0) Gecko/20100101 Firefox/48.0"}
        # 模拟浏览器进行访问
        request = urllib.request.Request(url=url, headers=header)
        context = ssl._create_unverified_context()
        response = urllib.request.urlopen(request, context=context)
        text = response.read().decode('utf-8')
        return text

    # 内容(标题+正文)
    def getContent(self, url):
        full_content = ''
        html = self.getHtml(url)
        # length = len(html)
        # print(html)
        pattern = re.compile(r'<section class="textblock">([\s\S]*?)<\/section>', re.RegexFlag.S)
        items_withtag = re.findall(pattern, html)
        for item in items_withtag:
            full_content += item;
        # writelog(full_content)
        return full_content

    def parseContent(self, url):
        res = html.parse(url).xpath("//div/@data-props")[0]
        data = json.loads(res)
        return data['data']['post']['summary']

    def get_news(self, url, title, summary):

        writelog("36kr，即将处理url：" + url)
        driver = self.create_phantomJS()
        driver.get(url)
        # 等待页面加载完成
        driver.implicitly_wait(30)
        page_src_code = driver.page_source
        # print(page_src_code)
        try:
            news = {}
            news['url'] = url
            news['author'] = u"36Kr"
            news['title'] = driver.title
            news['content'] = summary
            news['labels'] = "36kr默认标签"

            full_content = u""
            pattern = re.compile(r'<section class="textblock">([\s\S]*?)<\/section>', re.RegexFlag.S)
            items_withtag = re.findall(pattern, page_src_code)
            for item in items_withtag:
                full_content += item;
            # print(full_content)
            news['text'] = full_content

            textblock_element = driver.find_element_by_xpath('//section[@class="textblock"]')
            # print(textblock_element.text)
            # news['text'] = textblock_element.text

            driver.quit()

            writelog("36kr，处理正常结束！url：" + url)
            return news
        except Exception as e:
            writelog("36kr，解析出现异常！url=" + url)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            writelog("*** 异常堆栈如下:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=5, file=sys.stdout)
            writelog("-" *  100)
            return None



if __name__ == '__main__':

    # writelog(kr.get_news(url)['text'])

    kr = kr()
    url = 'https://36kr.com/api/search-column/23'
    inner_url_list = kr.get_inner_url_list_new(url)
    writelog(json.dumps(inner_url_list))
    for inner_url in inner_url_list:
        news = kr.get_news(inner_url['link'], inner_url['link'], inner_url['desc'])
        writelog("抓取到36kr文章：\n" + json.dumps(news))
