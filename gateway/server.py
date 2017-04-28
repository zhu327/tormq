# coding: utf-8
u"""
启动tornado服务
"""

import sys
import getopt
import tornado
from zmq.eventloop.ioloop import ZMQIOLoop
from handler import PushWebSocket
from hub import Hub

loop = ZMQIOLoop()
loop.install()


settings = {
    'xsrf_cookies': False,
    'debug' : True,
    'websocket_ping_interval': 60 # 定时发送ping, 保持心跳
}


app = tornado.web.Application([
    (r'/ws', PushWebSocket),
], **settings)


if __name__ == '__main__':
    port = '8000'
    remote = '127.0.0.1:5560' # MPC 消息发布中心 发布 地址

    opts, argvs = getopt.getopt(sys.argv[1:], 'r:p:')
    for op, value in opts:
        if op == '-r':
            remote = value
        if op == '-p':
            port = int(value)

    Hub(*remote.split(':'))

    app.listen(port)

    loop.start()