# Ayaka Uni

基于nonebot2改造而来（nonebot2虽然功能强大，但是我手头就一个QQ机器人而已，哪里需要那么多中间件、基类、跳来跳去

而且我对nonebot2的状态机也很不满意

# 拆解笔记

## nonebot.internal.adapter

### start_forward、stop_forward、_forward_ws

比较有意思

估计是用于web后端服务器使用，可以通过该方法，利用浏览器监控bot

虽然我删了

## nonebot2.exception
## nonebot2.matcher
## nonebot2.plugin
## nonebot2.dependencies
## nonebot2.permassion
## nonebot2.log
## nonebot2.rule

都需要被删除取代

## nonebot2.params

仍待研究

## nonebot2.adapters.onebot.v11.adapter

### _handle_api_result

检查超时情况，例如消息发送超时

## TYPE_CHECKING

估计是用来解决循环引用的一种方法，后面函数参数约束可以写"ClassName"

## 各种接口driver、adapter跳来跳去

估计也是为了解决循环引用，但是显然这种方法很傻逼，代码可阅读性为0

## 全部功能模块

> driver - fastapi
>
> 负责实现ws通信 setup_websocket_server


> adapter
>
> 负责监听driver传来的ws请求，创建相应bot，并连接bot和driver，driver只关心ws的实现，bot只关心高层的抽象（调用高级函数实现对应功能，获得已经处理好的event等）
>
> 原本adapter的设计可以允许多个cqhttp客户端向服务器端发起请求

> **event.py**
>
> 包含各种各样的事件，将json转换为对应的事件（事件内同时包含消息

> message
>
> 实现一个可以容纳多种类型内容的消息容器

bot 提供多样的高级函数，例如对群组发送消息、获取好友列表信息等；得益于cqhttp良好的接口定义，它们都基于call_api实现，且见名知义

> **logger.py**
>
> 基于Colorama自行实现一套漂亮的日志代码

assignment 处理消息，分发给各个插件

plugin 提供插件抽象

## 循环引用1.0

已知的几组循环有：

1. assignment <-> bot <-> adapter 相互引用

bot的高级方法依赖于adapter的api实现，adapter需要将ws收到的数据转化为event并传递给bot

bot需要将event和自身传递给assignment，assignment需要调用bot的方法实现功能

2. event <-> bot 一些event的方法需要调用bot（加好友请求）

3. template <-> message

driver 只负责提供ws通信方法，因此和adapter没有循环引用关系

logger、model、utils都是基础方法/类库

## 循环引用1.1

assignment <-> bot <-> adapter 相互引用 相互引用 已解套

通过更高层的ws流程控制解开 listen

ayaka._\_init__ -> listen -> bot, adapter, assignment



