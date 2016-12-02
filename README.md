### TORMQ

***

```
*************           *************            *************
*  client   *           *   client  *            *   client  *
*************           *************            *************
      |                        |                        |
      |                        |                        |
 *************          **************          **************
 * websocket *          *  websocket *          *  websocket *
 *    HUB    *          *     HUB    *          *      HUB   *
 *************          **************          **************
       \ sub                |  sub              sub/
        \                   |                     /
          ------------------|--------------------
                            | pub
                     ****************
                     *              *
                     *     MPC      *
                     *              *
                     ****************
                            | sub
          ------------------|-------------------
        /                   |                    \
      /                     |                      \
 ***********            **********               ************
 * sdk     *            * sdk    *               * sdk      *
 * service *            * http   *               * other... *
 ***********            **********               ************
```

Tormq 是基于Tornado ZeroMQ的开发的消息推送框架,具有高性能,高并发,高可用性,可伸缩扩容等特点.

Tormq 按模块可划分为3部分:

- MPC 消息发布中心,集中处理消息,是SDK,gateway的中介
- SDK 集成在业务系统中,用于发布消息,基于topic的订阅,可实现点对点或者广播消息推送
- gateway Tornado WebSocket 服务器,并且实现了Hub用于中转消息

### Example

#### MPC

```shell
python mpc.py -s 5559 -p 5560
```

- s: MPC 面向SDK发布者的端口
- p: MPC 面向gateway的端口

#### gateway

```shell
python gateway/server.py -r 127.0.0.1:5560 -p 8000
```

- r: 对接MPC的pub socket
- p: Tornado的WebSocket服务端口

#### SDK

```python
from sdk import Publisher

pub = Publisher('127.0.0.1', 5559)
pub.send('ehr:api', 'hello world') # 话题, 消息
```

#### WebSocket

```javascript
var s = new WebSocket('ws://localhost:8000/ws');

s.onopen = function(){
	this.send('{"event":"subscribe","topic":"ehr:api"}');
}

s.onmessage = function(v){
	console.log(v.data);
}
```

在建立WS连接后,需要发送订阅主题的action消息,SDK推送对应主题的消息,WS就会收到.

这里的订阅过程实现只是示例,具体的 认证/订阅/退订 的消息约定需要根据实际使用场景来设计.

比如需要发送推送消息:

```python
pub = Publisher('127.0.0.1', 5559)
pub.send('ehr', 'hello world') # 话题, 消息
```

所有订阅了以`ehr`为前缀topic的WS都会收到该消息.

### 特性

- 高并发
  - Tornado异步处理并发请求
  - pyzmq对Tornado异步回调的支持
  - Hub实现了订阅过程对MPC的解耦,通过inproc方式的订阅,支持更多订阅
- 高性能
  - ZeroMQ高性能网络消息框架
- 高可用
  - 得益于ZeroMQ的特性,无论是MPC SDK gateway 哪一个崩溃,都不会影响到整个消息系统的运行,只需要重启奔溃的部分即可
- 伸缩扩容
  - 在当前gateway实例已经不能满足并发量的前提下,可以横向增加gateway的实例数,并不会提高MPC的并发压力,因为每个gateway实例与MPC只有1个pub/sub连接