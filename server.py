#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import subprocess
import sys
import time

import psutil
from flask import Flask
from flask import request
from colorama import init, Fore

server = Flask(__name__)
# 任务服务器默认端口
server_port = 10086
# 任务 PID 图
task_map = {}
# 用于记录有延迟执行的任务
waiting_map = {}
# 初始化颜色
init(autoreset=True)


# 服务器状态 api
@server.route('/', methods=['GET'])
def server_status():
    return 'Task Server Running'


# 运行一个任务
@server.route('/add', methods=['GET'])
def add_task():
    # 获取参数 传入子进程
    params = ['python3', 'task.py']
    data_list = ['-d', '-u', '-s', '-t', '-p']
    # -p 持续时间
    # -t 任务执行间隔
    # -s 开始时间
    # -u 目标 url
    # -d 日志文件名称
    for data in data_list:
        if not request.values.get(data) is None:
            # 添加有延迟的任务到等待列表
            # 不太优雅 凑合吧
            if data == '-s':
                waiting_map[request.values.get('-d')] = \
                    time.mktime(time.strptime(request.values.get(data), '%Y-%m-%d %H:%M:%S'))
            params.append(data)
            params.append(request.values.get(data))
    try:
        task = subprocess.Popen(params)
    except Exception as e:
        return 'task submission failed. Error message' + str(e)
    task_map[request.values.get('-d')] = task
    return 'task submitted.'


# 删除一个任务
@server.route('/remove', methods=['GET'])
def remove_task():
    if request.values.get('task') in task_map.keys():
        task = task_map[request.values.get('task')]
        # 杀死任务
        task.kill()
    else:
        return 'task does not exist.'
    # 在图中移除
    del task_map[request.values.get('task')]
    return 'task removed.'


# 获取任务服务器 PID
@server.route('/pid', methods=['GET'])
def get_pid():
    return str(os.getpid())


# 获取任务状态
@server.route('/status', methods=['GET'])
def get_status():
    result = {}
    for task, ins in task_map.items():
        # 确实不优雅 :)
        if task in waiting_map.keys():
            if waiting_map[task] > time.time():
                result[task] = 'waiting'
            else:
                del waiting_map[task]
            continue
        process = psutil.Process(ins.pid)
        result[task] = str(process.status())
    return result


# 任务服务器
if __name__ == '__main__':
    print(Fore.YELLOW + 'The task server will run on port'
          , Fore.YELLOW + str(server_port)
          , Fore.YELLOW + 'do not allow external IP to access this port.')
    server.run(port=server_port)
