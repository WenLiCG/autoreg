# -*- coding:utf-8 -*-
import json
import sys

import requests
from colorama import init, Fore

# 任务服务器端口 需要与 server.py 保持一致
server_port = 10086
# 初始化颜色
init(autoreset=True)


# 检查服务器是否在线
def check_server_side_online():
    try:
        requests.get('http://127.0.0.1:' + str(server_port))
        return True
    except Exception as e:
        print(e)
        return False


# 获取服务端  PID
def get_server_pid():
    return requests.get('http://127.0.0.1:' + str(server_port) + '/pid').text


# 添加任务
def send_task(argv):
    data_dict = json.loads(requests.get('http://127.0.0.1:' + str(server_port) + '/status').text)
    params = {}
    for _count in range(1, len(sys.argv), 2):
        # 判断任务列表是否存在相同的任务
        if argv[_count] == '-d':
            if argv[_count + 1] in data_dict.keys():
                return Fore.YELLOW + 'duplicate task submission. please do not submit the same task name.'
        # 拼接参数
        params[argv[_count]] = argv[_count + 1]
    return requests.get('http://127.0.0.1:' + str(server_port) + '/add', params=params).text


# 移除任务
def remove_task(task):
    return requests.get('http://127.0.0.1:' + str(server_port) + '/remove?task=' + task).text


# 显示任务
def list_task():
    data_dict = json.loads(requests.get('http://127.0.0.1:' + str(server_port) + '/status').text)
    # 展示列表
    print('task', '\t\t', 'status')
    for key, value in data_dict.items():
        if value == 'running':
            print(key, '\t', Fore.GREEN + 'running')
        elif value == 'zombie':
            print(key, '\t', Fore.RED + 'zombie')
        elif value == 'waiting':
            print(key, '\t', Fore.YELLOW + 'waiting')
        elif value == 'done':
            print(key, '\t', Fore.BLUE + 'done')
        else:
            print(key, '\t', value)


# 根据参数启动任务
# -d 创建任务 同时也是日志名
# -p 持续时间 单位 m h 如 3h5m 代表 三小时五分钟
# -t 任务执行间隔 单位 秒 可以是小数 比如 0.1 是 100 毫秒
# -s 开始时间 格式 %Y-%m-%d %H:%M:%S 如 2022-01-01 00:00:00
# -u 目标 url
# -r 移除已创建任务
# -l 任务列表
if __name__ == '__main__':
    # 判断服务器侧是否在线
    if not check_server_side_online():
        print(Fore.RED + 'task server offline. use python server.py or python3 server.py boot server.')
        sys.exit()
    for count in range(0, len(sys.argv)):
        arg = sys.argv[count]
        if arg == '-d':
            print(send_task(sys.argv))
        if arg == '-r':
            print(remove_task(sys.argv[count + 1]))
        if arg == '-l':
            print('TASK SERVER PID', get_server_pid())
            list_task()
