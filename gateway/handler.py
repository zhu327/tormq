# coding: utf-8
u"""
tornado WebSocket handler
挂接WebSocket连接到ZeroMQ连接上
"""

import json
from tornado import websocket
from tornado.log import app_log
from hub import Subscriber


class PushWebSocket(websocket.WebSocketHandler):
    u"""
    消息推送WebSocket连接
    """
    def check_origin(self, origin):
        u"""
        跨域检查

        在这里可以考虑做token认证
        通过self.request.headers可以拿到ws初始http请求头
        如果认证不通过直接拒绝连接
        """
        return True

    def open(self):
        u"""
        如果在check_origin做了认证
        可以在连接open后直接self.sub.subscribe()订阅默认用户id的topic
        """
        self.sub = Subscriber(self.push)

    def on_message(self, message):
        app_log.debug('client message: {}'.format(message))
        # to-do: 定义 订阅/退订 消息格式
        try:
            content = json.loads(message)
            event = content['event']
            if event == 'subscribe':
                u'''
                更新订阅topic
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
                {"event": "unsubscribe",}
                '''
                self.sub.unsubscribe()
            else:
                pass
        except:
            pass

    def on_close(self):
        if hasattr(self, 'sub'):
            self.sub.close()
        app_log.debug('connection close')

    def push(self, msg):
        if self.ws_connection:
            self.write_message(msg)
