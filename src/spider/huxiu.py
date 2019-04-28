# _*_encoding:utf-8_*_

import requests

import sys, traceback

import urllib.request

import urllib.parse

import re

from lxml import html

import ssl

import json

sys.path.append("..")
from Write_Log import writelog


class huxiu(object):
    def __init__(self):
        self.base_url = 'https://www.huxiu.com'
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
            writelog("huxiu，网络请求发生错误，请检查! url:" + url)

    def get_inner_url_list(self, url):
        """
        : param
        : return: url_list  返回从频道首页通栏中的文章的url
        """
        writelog("huxiu开始解析原始URL:" + url)

        selector = self.parser(url)
        url_tmp_list = list(set(selector.xpath('//*[@id="index"]//div[@class="mod-info-flow"]//div[@class="mob-ctt channel-list-yh"]//a[@class="transition msubstr-row2"]/@href')))
        """
        : param: url {'/article/220006.html', '/article/219989.html', '/article/220008.html'}
        添加url，获取完整的url地址。
        """
        url_list = []
        for url_tmp in url_tmp_list:
            full_url_tmp = self.base_url + url_tmp
            url_list.append(full_url_tmp)

        writelog("huxiu返回inner_url_list内容如下:\n" + json.dumps(url_list) + "\n")

        return url_list

    def get_inner_url_list_new(self, url):
        writelog("====>>>> huxiu开始解析原始URL:{}\n".format(url))
        inner_url_list = []
        selector = self.parser(url)
        for sel in selector.xpath("//*[@id='index']//div[@class='mod-info-flow']/div[@class='mod-b mod-art clearfix']"):
            item = {}
            title_datas = sel.xpath("div[@class='mob-ctt channel-list-yh']/h2/a/text()")
            item['title'] = '' + title_datas[0]
            link_datas = sel.xpath("div[@class='mob-ctt channel-list-yh']/h2/a/@href")
            item['link'] = self.base_url + link_datas[0]
            desc_datas = sel.xpath("div[@class='mob-ctt channel-list-yh']/div[@class='mob-sub']/text()")
            item['desc'] = '' + desc_datas[0]
            img_datas = sel.xpath("div[@class='mod-thumb pull-left ']/a[@class='transition']/img[@class='lazy']/@data-original")

            # 头图是视频缩略图时，xpath解析较复杂，暂跳过
            if img_datas == False:
                continue;
            if len(img_datas) == False :
                continue;

            item['img'] = '' + img_datas[0]
            inner_url_list.append(item)

        # writelog("huxiu返回inner_url_list:{}\n".format(json.dumps(inner_url_list)))
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
        # writelog(html)
        # pattern = re.compile('<h1 class="headline-title">(.*?)</h1>')
        # items = re.findall(pattern, html)
        # writelog(items[0])
        # 匹配文章内容
        # re.S匹配换行符

        pattern = re.compile(r'<div id=".*?" class="article-content-wrap">([\s\S]*?)<\/div>', re.RegexFlag.S)
        # pattern = re.compile(r'class="article-content-wrap">(.*?)</div>', re.RegexFlag.S)
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
        writelog("huxiu，即将处理url：" + url)
        news = {}
        flag = None
        try:
            # 重新组合成https://m.huxiu.com/ 类型的移动端url地址。
            news['url'] = url
            news['link'] = url[0:8:1] + "m" + url[11:-1:1] + url[-1]
            selector = self.parser(url)
            news['title'] = selector.xpath('/html/head/title/text()')[0].replace('-虎嗅网', '')
            news['author'] = u'虎嗅网'
            # selector.xpath('//div[3]/div[1]/div[2]/a[1]/text()')[0].strip()

            content = selector.xpath('//div[@class="article-content-wrap"]//p')

            article = ""
            temp = []
            for i in content:
                img_url = i.xpath('img/@src')
                temp.append(i.text)
                temp.append(img_url)

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

            news['content'] = summary.replace('\xa0', '')

            full_article = self.getContent(url)
            # full_article_list = selector.xpath('//div[@class="article-content-wrap"]')
            # for tmp_full_article in full_article_list:
            #    tmp_article_value = tmp_full_article.string()
            #    writelog(tmp_article_value)

            # news['text'] = article
            news['text'] = full_article
            labels_list = selector.xpath('//div[@class="article-img-box"]/img/@src')
            if labels_list:
                news['labels'] = "" + labels_list[0]
            else :
                writelog("huxiu，无法解析标签！url=" + url)
                news['labels'] = "虎嗅网默认标签"
            labels_list = selector.xpath('//div[@class="column-link-box"]/a/text()')
            if labels_list:
                news['labels'] = ""
                for label in labels_list:
                    news['labels'] += (" " + label)
            else :
                news['labels'] = "虎嗅网默认标签"
            news['service'] = 'Article.AddArticle'
        except Exception as e:
            writelog("huxiu，解析出现异常！url=" + url)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            writelog("*** 异常堆栈如下:")
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=5, file=sys.stdout)
            writelog("-" *  100)
            flag = 1

        if flag == None:
            writelog("huxiu，处理正常结束！url：" + url)
            return news
        else:
            return None

if __name__ == '__main__':
    huxiu = huxiu()

    url = 'https://www.huxiu.com/channel/104.html'
    inner_url_list = huxiu.get_inner_url_list_new(url)

    for inner_url in inner_url_list:
        huxiu.get_news(inner_url['link'])