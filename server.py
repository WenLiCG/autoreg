# -*- coding:utf-8 -*-
import os
import re
import subprocess
import sys
import threading
import time

import psutil
from flask import Flask
from flask import request
from colorama import init, Fore

# 解析时间的正则
hour_pattern = re.compile(r'\d+h')
min_pattern = re.compile(r'\d+m')
# 初始化服务器
server = Flask(__name__)
# 任务服务器默认端口
server_port = 10086
# 任务图 key 任务名 value 任务实例
task_map = {}
# 任务状态图 key 任务名 value 任务状态
status_map = {}
# 线程图
thread_status = {}
# 表示任务还在运行开始到任务介绍之间的时间内
running = {}
# 初始化颜色
init(autoreset=True)


def task(name, start, online, params):
    # 任务前休眠时间
    # 获得 Unix 时间戳后相减得到 sleep 秒数
    start = time.mktime(time.strptime(start, '%Y-%m-%d %H:%M:%S'))
    now = time.time()
    # 休眠到预定时间 但 start 总不能是个过去的时间吧
    if start > now:
        status_map[name] = 'waiting'
        time.sleep(start - now)
    # 判断任务是否移除
    if name not in thread_status.keys():
        return
    if name in thread_status.keys() and (thread_status[name] is False):
        del thread_status[name]
        return
    # 执行任务后休眠
    try:
        running_task = subprocess.Popen(params)
        status_map[name] = 'running'
        task_map[name] = running_task
    except Exception as e:
        status_map[name] = 'zombie'
        return 'task submission failed. Error message' + str(e)
    # 判断任务是否移除
    if name not in thread_status.keys():
        return
    if name in thread_status.keys() and (thread_status[name] is False):
        del thread_status[name]
        return
    # 等待任务结束
    running[name] = True
    hour = int(0 if hour_pattern.search(online) is None
               else hour_pattern.search(online).group().replace('h', ''))
    minute = int(0 if min_pattern.search(online) is None
                 else min_pattern.search(online).group().replace('m', ''))
    time.sleep(hour * 3600 + minute * 60)
    status_map[name] = 'done'
    # 判断任务是否移除
    if name in thread_status.keys() and (thread_status[name] is False):
        del thread_status[name]
    # 移出运行时间
    if name in running.keys():
        del running[name]
    running_task.kill()


# 服务器状态 api
@server.route('/', methods=['GET'])
def server_status():
    return 'Task Server Running'


# 运行一个任务
@server.route('/add', methods=['GET'])
def add_task():
    # 获取参数 传入子进程
    params = ['python3', 'task.py']
    # -p 持续时间
    # -t 任务执行间隔
    # -s 开始时间
    # -u 目标 url
    # -d 日志文件名称
    data_list = ['-d', '-u', '-s', '-t', '-p']
    # 任务名
    name = ''
    # 开始时间
    start_time = ''
    # 运行时间
    online = ''

    for data in data_list:
        if not request.values.get(data) is None:
            if data == '-d':
                name = request.values.get(data)
            if data == '-s':
                start_time = request.values.get(data) if not request.values.get(data) == 'now' \
                    else '1970-01-01 00:00:00'
            if data == '-p':
                online = request.values.get(data)
            params.append(data)
            params.append(request.values.get(data))
    thread_status[name] = True
    start_time = start_time if not start_time == '' else '1970-01-01 00:00:00'
    thread = threading.Thread(target=task, args=(name, start_time, online, params))
    thread.start()
    return 'task submitted.'


# 删除一个任务
@server.route('/remove', methods=['GET'])
def remove_task():
    name = request.values.get('task')
    # 判断任务是否存在
    if name not in status_map.keys():
        return 'task not found.'
    # 结束任务进程
    if name in task_map.keys():
        task_process = task_map[name]
        task_process.kill()
        del task_map[name]
    # 移除任务状态
    del status_map[name]
    # 设置线程标志
    # 判断任务是否移除
    thread_status[name] = False
    return 'task removed.'


# 获取任务服务器 PID
@server.route('/pid', methods=['GET'])
def get_pid():
    return str(os.getpid())


# 获取任务状态
@server.route('/status', methods=['GET'])
def get_status():
    result = {}
    for name, status in status_map.items():
        if name in (task_map.keys() and running.keys()) \
                and (psutil.Process(task_map[name].pid).status() not in ['running', 'sleeping']):
            status_map[name] = psutil.Process(task_map[name].pid).status()
            thread_status[name] = False
            del thread_status[name]
            result[name] = psutil.Process(task_map[name].pid).status()
            continue
        result[name] = status
    return result


# 任务服务器
if __name__ == '__main__':
    print(Fore.YELLOW + 'The task server will run on port'
          , Fore.YELLOW + str(server_port)
          , Fore.YELLOW + 'do not allow external IP to access this port.')
    server.run(port=server_port)

