# coding: utf-8
u"""
消息发布 sdk
向 MPC 消息发布中心发布消息

from sdk import Publisher

pub = Publisher('127.0.0.1', 5559)
pub.send()
"""
import time
import json
import zmq

__all__ = ('Publisher',)

context = zmq.Context()


class Publisher(object):
    u"""
    sdk 消息发布者
    host: MPC host
    port: MPC sub port, default 5559
    """
    def __init__(self, host, port):
        self.sock = context.socket(zmq.PUB)
        self.sock.connect('tcp://{}:{}'.format(host, port))
        time.sleep(0.2)

    def send(self, topic, body):
        u"""
        发送消息,具体实现需要设计消息格式
        """
        top = topic.split(':')[0]
        msg = {
            'topic': topic,
            'data': body
        }
        self.sock.send_multipart([top, json.dumps(msg, ensure_ascii=False)])

    def __del__(self):
        if hasattr(self, 'sock') and isinstance(self.sock, context._socket_class):
            self.sock.close()