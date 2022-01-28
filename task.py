# -*- coding:utf-8 -*-
import logging
import os
import sys
import time
import threading

import requests

# 任务执行间隔
delay = ''
# 目标 URL
url = ''
# 日志文件名
log = 'common.log'


# 单独线程请求 api
def request_api():
    try:
        logging.info(requests.get(url, timeout=5).text)
    except requests.exceptions.ConnectTimeout as timeout:
        logging.info('this request timeout.')
    except Exception as e:
        logging.info(e)


# 任务服务器
# -p 持续时间
# -t 任务执行间隔
# -s 开始时间
# -u 目标 url
# -d 日志文件名称
if __name__ == '__main__':
    # 循环读取参数
    for count in range(0, len(sys.argv)):
        arg = sys.argv[count]
        if arg == '-t':
            delay = sys.argv[count + 1]
        if arg == '-u':
            url = sys.argv[count + 1]
        if arg == '-d':
            log = sys.argv[count + 1]

    # 自动创建目录文件
    if not os.path.exists('./log'):
        os.makedirs('./log')
    # 日志配置
    logging.basicConfig(level=logging.DEBUG, filename=('./log/' + log + '.log'), filemode="w",
                        format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    # 任务进行中
    while True:
        threading.Thread(target=request_api).start()
        time.sleep(float(delay))
