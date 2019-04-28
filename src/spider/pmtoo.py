# _*_encoding:utf-8_*_

import requests

import sys, traceback

import urllib.request

import urllib.parse

import re

from lxml import html

import json

sys.path.append("..")
from Write_Log import writelog


class pmtoo(object):
    def __init__(self):
        self.base_url = 'http://www.pmtoo.com'
        # self.url = 'http://www.pmtoo.com/article/category/产品经理'
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate", "Accept-Language": "zh-CN,zh;q=0.8", "Cache-Control": "max-age=0",
            "Connection": "keep-alive", "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36", }
        self.session = requests.session()

    def parser(self, url):
        """
        : param url: 需要解析页面的url地址
        : return: selector
        """
        response = self.session.get(url=url, headers=self.headers, verify=True)
        if response.status_code == 200:
            selector = html.fromstring(response.text)
            return selector
        else:
            writelog("pmtoo，网络请求出现异常，请检查! url:" + url)

    def get_inner_url_list(self, url):
        """
        : param
        : return: url_list  返回从频道首页通栏中的文章的url
        """

        writelog("pmtoo开始解析原始URL:" + url)

        selector = self.parser(url)
        url_tmp_list = list(set(selector.xpath('//h2[@class="title"]/a/@href')))
        """
        : param: url {'/article/220006.html', '/article/219989.html', '/article/220008.html'}
        添加url，获取完整的url地址。
        """
        url_list = []
        for url_tmp in url_tmp_list:
            url_list.append(url_tmp)

        writelog("pmtoo返回inner_url_list内容如下:\n" + json.dumps(url_list) + "\n")

        return url_list

    # 获取网页源码
    def getHtml(self, url):
        header = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:48.0) Gecko/20100101 Firefox/48.0"}
        # 模拟浏览器进行访问
        request = urllib.request.Request(url=url, headers=header)
        response = urllib.request.urlopen(request)
        text = response.read().decode('utf-8')
        return text

    # 内容(标题+正文)
    def getContent(self, url):
        full_content = ''
        html = self.getHtml(url)
        # writelog(html)
        #pattern = re.compile('<h1 class="headline-title">(.*?)</h1>')
        #items = re.findall(pattern, html)
        # writelog(items[0])
        # 匹配文章内容
        # re.S匹配换行符

        pattern = re.compile(r'<div id=".*?" class="post-con mobantu">([\s\S]*?)<\/div>', re.RegexFlag.S)
        items_withtag = re.findall(pattern, html)
        for item in items_withtag:
            # 去除标签正则
            # dr = re.compile(r'<[^>]+>', re.S)
            # dd = dr.sub('', item)
            # writelog(dd)
            # writelog(item)
            full_content += item;
        # writelog(full_content)
        return full_content

    def get_news(self, url):
        """
        : param
        url : 需要进行获取信息的url地址
        flag : 标志位，判断是否抓取成功
        news : 字典，存储各信息
        : return: news 正常返回news，错误返回 -1
        """
        writelog("pmtoo，即将处理url：" + url)
        news = {}
        flag = None
        try:
            news['url'] = url
            selector = self.parser(url)
            title = selector.xpath('/html/head/title/text()')[0]
            news['author'] = u'产品中国'

            tmp = ""
            for i in title:
                if i == '–':
                    break
                tmp += i
            news['title'] = tmp

            content = selector.xpath('//div[@class="post-con mobantu"]//p')

            article = ""
            temp = []
            cover_list = []
            for i in content:
                img_url = i.xpath('img/@src')
                temp.append(i.text)
                temp.append(img_url)
                cover_list.append(img_url)

            # 去除尾部多余信息
            for i in range (4):
                temp.pop ()

            for i in temp:
                if i:
                    if type(i) == list:
                        article = article + "\n" + "![](" + i[0] + ")" + "\n\n"
                    else:
                        article = article + i + "\n\n"

            summary = ""
            for i in temp:
                if len(summary) > 400:
                    break
                else:
                    if i:
                        if type(i) == list:
                            pass
                        else:
                            summary = summary + i + "\n"

            news[ 'content' ] = summary

            full_article = self.getContent(url)
            news['text'] = full_article
            # news['text'] = article

            for i in cover_list:
                if i:
                    news['cover'] = i[0]
                    break

            news['labels'] = u"产品中国"
        except Exception as e:
            writelog("pmtoo，解析时出现异常，请检查！url=" + url)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            writelog("*** print_exception:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=5, file=sys.stdout)
            writelog("-" *  100)
            flag = 1

        if flag == None:
            writelog("pmtoo，处理正常结束！url=" + url)
            return news
        else:
            return None


if __name__ == '__main__':
    spider = pmtoo()

    url = 'http://www.pmtoo.com/article/category/产品经理'
    inner_url_list = spider.get_inner_url_list(url)
    writelog("产品中国inner_url_list:" + json.dumps(inner_url_list))
    for inner_url in inner_url_list:
        writelog("产品中国news:" + json.dumps(spider.get_news(inner_url)))