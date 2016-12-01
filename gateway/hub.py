# coding: utf-8

import os
import json
import re
import zmq
from zmq.eventloop.zmqstream import ZMQStream
from tornado.log import app_log

pid = os.getpid()
context = zmq.Context()


class Hub(object):
    u"""
    本地消息中心
    获取MPC发布的消息,并发送到WebSocket绑定的socket上

    此类为一个本地的pub/sub-HUB,任何新websocket连接进来都会通过一个zmqsocket订阅到HUB
    的pub端,与此同时这个HUB自己也会订阅一个真正的消息中心MPC

    websocket连接中通过ipc连接协议订阅HUB

    HUB通过tcp连接协议订阅MPC
    """
    def __init__(self, host, port):
        self.sub = context.socket(zmq.SUB)
        self.sub.setsockopt(zmq.SUBSCRIBE, '')
        self.sub.connect('tcp://{}:{}'.format(host, port))

        self.local_pub = context.socket(zmq.PUB) # 本地发布者绑定inproc进程间通信
        self.local_pub.bind('inproc:///tmp/hub_{}'.format(pid))

        self.substream = ZMQStream(self.sub)
        self.substream.on_recv(self.recv)

    def recv(self, msg):
        app_log.info('Message: {}'.format(msg))
        self.local_pub.send_multipart(msg)


class Subscriber(object):
    u"""
    本地订阅者
    订阅topic匹配关系

    订阅 ehr:api:1
    匹配消息 'ehr', 'ehr:api', 'ehr:api:1'

    实现直连推送,或者广播
    """
    def __init__(self, callback):
        self.callback = callback
        self.topic = ''

        self.sock = context.socket(zmq.SUB)
        self.sock.connect('inproc:///tmp/hub_{}'.format(pid))

        self.stream = ZMQStream(self.sock)
        self.stream.on_recv(self.recv)

    def subscribe(self, topic):
        if not isinstance(topic, basestring) or not topic:
            return

        self.topic = topic
        self.sock.setsockopt(zmq.SUBSCRIBE, str(topic.split(':')[0]))

    def unsubscribe(self):
        if self.topic:
            self.sock.setsockopt(zmq.UNSUBSCRIBE, str(self.topic.split(':')[0]))
            self.topic = ''

    def recv(self, msg):
        _, body = msg
        try:
            data = json.loads(body)
            topic = data.get('topic', '')
            if not topic:
                return
            if re.match(r'^{}(:.+)?$'.format(topic), self.topic):
                self.callback(body)
        except:
            pass

    def close(self):
        self.topic = None
        self.callback = None
        self.stream.close()