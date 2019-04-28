#_*_encoding:utf-8_*_

import time

def time_now():
    time_now = time.strftime('%Y-%m-%d %H:%M:%S  ', time.localtime(time.time()))
    return time_now

def writelog(text):
    file_name = 'log.txt'
    with open(file_name, 'a+', encoding='utf-8') as f:
        f.write(time_now() + text + '\n')


if __name__ == '__main__':
    writelog("测试日志功能")