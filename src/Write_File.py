#_*_encoding:utf-8_*_

import time

def time_now():
    time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    return time_now

def write(news):
    file_name = 'articles.txt'
    with open(file_name, 'a+', encoding='utf-8') as f:
        text = "<!--markdown-->" + news['text']
        articleContent = "\n标题：" + news['title'] + "\n作者：" + news['author'] + "\n正文：\n " + text
        f.write(articleContent)



if __name__ == '__main__':
    news = {'url': 'https://www.huxiu.com/article/227432.html', 'link': 'https://m.huxiu.com/article/227432.html', 'title': '京东金融，四年追击 ', 'author': '虎嗅网', 'labels': '金融地产', 'service': 'Article.AddArticle'}
    write(news)