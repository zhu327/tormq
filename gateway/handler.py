# coding: utf-8
u"""
tornado WebSocket handler
挂接WebSocket连接到ZeroMQ连接上
"""

import time
import json
from tornado import websocket
from tornado.log import app_log
from hub import Subscriber

HEARTBEAT_CYCLE = 60
CONNECTION_COUNT = 0


class PushWebSocket(websocket.WebSocketHandler):
    u"""
    消息推送WebSocket连接
    """
    def check_origin(self, origin):
        return True

    def open(self):
        self.sub = Subscriber(self.push)
        self.timestamp = time.time()
        global CONNECTION_COUNT
        CONNECTION_COUNT += 1
        app_log.info('online connections {}'.format(CONNECTION_COUNT))

    def on_message(self, message):
        app_log.debug('client message: {}'.format(message))
        self.timestamp = time.time()
        # to-do: 定义 认证/订阅/退订 消息格式
        try:
            content = json.loads(message)
            event = content['event']
            if event == 'authenticate':
                u'''
                {
                    "event": "authenticate",
                    "token": "auth-token",
                    "topic": "ehr:api"
                }
                认证并重组订阅topic: ehr:api:{user_id}
                '''
                pass # 具体认证实现依赖于应用
            elif event == 'subscribe':
                u'''
                订阅
                {
                    "event": "subscribe",
                    "topic": "ehr:api"
                }
                '''
                topic = content['topic']
                self.sub.subscribe(topic)
            elif event == 'unsubscribe':
                u'''
                退订
                {
                    "event": "unsubscribe",
                }
                '''
                self.sub.unsubscribe()
            elif event == 'ping':
                u'''
                ping
                {
                    "event": "ping",
                }
                '''
                pass
        except:
            pass

    def on_close(self):
        if hasattr(self, 'sub'):
            self.sub.close()
        global CONNECTION_COUNT
        CONNECTION_COUNT -= 1
        app_log.info('online connections {}'.format(CONNECTION_COUNT))

    def push(self, msg):
        if (time.time() - self.timestamp > 2 * HEARTBEAT_CYCLE):
            # 如果在2个心跳周期内没有收到ping,关闭连接
            self.close()
        else:
            self.write_message(msg)
