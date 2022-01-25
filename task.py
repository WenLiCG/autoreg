#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import logging
import os
import re
import sys
import time
import threading

import requests

# 持续时间
online = ''
# 任务执行间隔
delay = ''
# 开始时间
start = ''
# 目标 URL
url = ''
# 日志文件名
log = 'common.log'
# 进程结束信号
kill_signal = False
# 解析时间的正则
hour_pattern = re.compile(r'\d+h')
min_pattern = re.compile(r'\d+m')


# 单独线程请求 api
def request_api():
    try:
        logging.info(requests.get(url, timeout=5).text)
    except requests.exceptions.ConnectTimeout as timeout:
        logging.info('this request timeout.')
    except Exception as e:
        logging.info(e)


# 循环主线程
def runner():
    while True:
        if kill_signal:
            print('task', log, 'done.')
            sys.exit()
        threading.Thread(target=request_api).start()
        time.sleep(float(delay))


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
        if arg == '-p':
            online = sys.argv[count + 1]
        if arg == '-t':
            delay = sys.argv[count + 1]
        if arg == '-s':
            start = sys.argv[count + 1]
        if arg == '-u':
            url = sys.argv[count + 1]
        if arg == '-d':
            log = sys.argv[count + 1]
    # 日志配置

    dirs = './log'
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    logging.basicConfig(level=logging.DEBUG
                        , filename=('./log/' + log + '.log')
                        , filemode="w"
                        , format="%(asctime)s - %(message)s"
                        , datefmt="%Y-%m-%d %H:%M:%S"
                        )
    # 调度器
    if start == '' or start == 'now':
        requester = threading.Thread(target=runner)
        requester.start()
    else:
        # 获得 Unix 时间戳后相减得到 sleep 秒数
        start = time.mktime(time.strptime(start, '%Y-%m-%d %H:%M:%S'))
        now = time.time()
        # 休眠到预定时间 但 start 总不能是个过去的时间吧
        if start > now:
            time.sleep(start - now)
        requester = threading.Thread(target=runner)
        requester.start()
    # 任务进行中
    print('task', log, 'working...')
    # 执行线程后计算运行时间
    if not online == '':
        hour = int(0 if hour_pattern.search(online) is None
                   else hour_pattern.search(online).group().replace('h', ''))
        minute = int(0 if min_pattern.search(online) is None
                     else min_pattern.search(online).group().replace('m', ''))
        time.sleep(hour * 3600 + minute * 60)
        kill_signal = True
    else:
        kill_signal = True
