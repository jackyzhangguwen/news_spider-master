#_*_encoding:utf-8_*_

import time

import pymysql

import hashlib

import configparser

from Write_Log import writelog

def time_now():
    time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    return time_now

def writeIntoMysql(news, web_src_id, web_src_name, web_platform_id, img, desc):
    # 打开数据库连接
    cfg = configparser.ConfigParser()
    cfg.read("conf.ini")
    db_host = cfg.get("database", "host")
    db_port = cfg.getint("database", "port")
    db_name = cfg.get("database", "dbname")
    db_user = cfg.get("database", "user")
    db_pass = cfg.get("database", "pass")

    db = pymysql.connect(host=db_host, user=db_user, password=db_pass,db=db_name,port=db_port, use_unicode=True, charset="utf8")
    cur = db.cursor()

    try:
        str = news['url']
        hashlibMd5 = hashlib.md5()
        hashlibMd5.update(str.encode(encoding='utf-8'))
        id = hashlibMd5.hexdigest()

        # 新增91_article记录
        sql_insert1 = "insert into 91_article(id,create_by,create_date,title,keywords,image,websrc_id,websrc_name,web_platform_id,description) values(%s,%s,now(),%s,%s,%s,%s,%s,%s,%s)"
        values1 = (id, "webcrawler", news['title'], news['labels'], img, web_src_id, web_src_name, web_platform_id, desc)
        cur.execute(sql_insert1, values1)

        # 新增91_article_data记录
        sql_insert2 = "insert into 91_article_data(id,content,copyfrom) values(%s,%s,%s)"
        values2 = (id, news['text'], news['author'])
        cur.execute(sql_insert2, values2)
        # 提交
        db.commit()
    except Exception as e:
        # 错误回滚
        db.rollback()
        writelog("数据库写入失败!异常原因：{}\n".format(e))
        return False
    finally:
        cur.close()
        db.close()

    writelog("数据库写入成功!\n")
    return True


def is_url_processed(url) :
    str = url
    hashlibMd5 = hashlib.md5()
    hashlibMd5.update(str.encode(encoding='utf-8'))
    id = hashlibMd5.hexdigest()
    # 打开数据库连接
    cfg = configparser.ConfigParser()
    cfg.read("conf.ini")
    db_host = cfg.get("database", "host")
    db_port = cfg.getint("database", "port")
    db_name = cfg.get("database", "dbname")
    db_user = cfg.get("database", "user")
    db_pass = cfg.get("database", "pass")

    db = pymysql.connect(host=db_host, user=db_user, password=db_pass,db=db_name,port=db_port, use_unicode=True, charset="utf8")
    cur = db.cursor()
    sql_select_from_article = "select 1 as cnt from 91_article where id=%s"
    values = (id)
    result_data = cur.execute(sql_select_from_article, values)

    cur.close()
    db.close()

    if result_data > 0  :
       writelog("该url已存在数据库中：{}\n".format(url))
       return True

    return False


if __name__ == '__main__':
    news = {'url': 'https://www.huxiu.com/article/227432.html', 'link': 'https://m.huxiu.com/article/227432.html', 'title': '京东金融，四年追击 ', 'labels': '互联网,金融', 'author': '虎嗅网', 'text': '金融地产金融地产金融地产金融地产金融地产金融地产金融地产金融地产金融地产金融地产金融地产金融地产金融地产金融地产金融地产', 'service': 'Article.AddArticle'}
    writeIntoMysql(news, '11', '22', '33', '44', '55')