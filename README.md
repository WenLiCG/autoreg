# autoreg

### 安装
系统基于debian 10,其他debian应该也可以
```
apt-get update && apt-get install -y screen python3 python3-pip
pip3 install -r requirements.txt
pip3 install gunicorn
```


### 实例
先在后台运行这条命令启动服务端,建议配合screen或者其他后台运行命令(autoreg目录下)
```
screen -d -m gunicorn -b 127.0.0.1:10086 server:server
```
然后
```
python3 autoreg.py -d google.com -s '2022-01-18 13:00:00' -p 10m -t 2 -u 'https://xxxxxxxx'
```
命令:-d 创建任务名为google.com,并且记录log到名为google.com的文件中

命令:-s 从2022-01-18 13:00:00就开始发送http请求(忽略此命令就立刻开始,时间早于系统时间也立刻开始)

命令:-p 持续10分钟

命令:-t 每个2秒发送一次

命令:-u http请求为: http://xxxxxxx

其他命令

命令:-l 显示当前所有任务

命令:-r 删除某任务


### API申请
推荐使用dynadot的API,简单! [点我申请账号](http://www.dynadot.com/?s9R7O6J9A6We7Q7A)

申请完账号后在 Tools->API中就能创建API,替换下面链接的xxxxxxxxxxx,在把google.com替换成自己想要的域名就可以了
```
https://api.dynadot.com/api3.xml?key=xxxxxxxxxxx&command=register&domain=google.com&duration=1&currency=USD
```
### 注意
请求间务必大于1秒,不然容易被封API,也不要长时间占用API


### 以后准备的更新
1.如果添加多任务很容易同时发送很多API请求,API的请求间隔不应该设置到单任务中,应该统一管理.

2.重启后任务都会消失,需要设置任务记录保存,重启后继续进行


## Collaborators

[Hanbings](https://github.com/Hanbings)
