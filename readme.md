# Ayaka Uni

基于 nonebot2 改造而来（nonebot2 虽然功能强大，但是我手头就一个 QQ 机器人而已，哪里需要那么多中间件、基类、跳来跳去

而且我对 nonebot2 的状态机也很不满意

# 安装方法

```bash
# install
poetry install
# 不同系统上一些包的依赖也可能不一样，因此如果运行时提示某些包缺失，自己装上就好（乐）

# start
poetry run python bot.py
```

配置 cqhttp 为反向 ws，地址为 ws://127.0.0.1:19900/ayakabot

# 插件编写

```python
from ayaka.lazy import *
from ayaka.div import div_cmd_arg

app = AyakaApp(name="test")
app.help = {
    "idle": "啊",
    "test": "复读机"
}

# help可以是字典形式，不同的key对应不同的state
# help也可以是字符串形式，对于没有状态机要求的插件来说，可以直接写字符串，不必加idle作为键名


# 仅当idle状态时生效
@app.command(["测试", "test"], "idle")
async def handle(bot: Bot, event, device: AyakaDevice):
    # 通知device, app开始运行
    success, info = device.start_app(app.name)
    if success:
        # 跳转到test状态
        app.set_state(device, "test")

    # 开启成功/失败
    await bot.send(event, info)


# 仅当test状态时生效
@app.command(["退出", "exit"], "test")
async def handle(bot: Bot, event, device: AyakaDevice):
    # 通知device, app结束运行
    success, info = device.stop_app()

    # 跳转到idle状态
    app.set_state(device, "idle")

    # 开启成功/失败
    await bot.send(event, info)


# 仅当test状态时生效
@app.message("test")
async def handle(bot: Bot, event: GroupMessageEvent, device):
    try:
        i = int(event.get_plaintext())
    except:
        # 复读机
        await bot.send(event, event.get_plaintext())
    else:
        s = "s"*i
        await bot.send(event, s)
        await bot.send_group_forward_msg(event.group_id, [s])

    # 告知系统该message被该插件使用
    return True


# 当idle、test状态时都生效
@app.command(["复读", "repeat"], ["idle", "test"])
async def handle(bot: Bot, event: GroupMessageEvent, device):
    # arg为 排除了命令外的所有参数 的 字符串之和
    cmd, args, arg = div_cmd_arg(["复读", "repeat"], event.message)

    # 复读第二个参数
    if len(args) >= 2:
        await bot.send(event, args[1])
    else:
        await bot.send(event, "参数不够多")



```

## device

一个群聊就是一个`device`

一个`device`同一时间只能运行一个`app`，通过`start_app`和`stop_app`控制，它们会返回`bool`值和设备提示信息

通过`device.id`或`event.group_id`均获取群聊 id，但是要注意，在跨群聊插件中，这两者可能不一致，此时应以`device.id`为准

保留`device`的设计是为了后续拓展跨群组应用做铺垫，例如：

小明在群组 A 中发起了匿名投票，投票人 B 可私聊机器人，告知投票结果，实现匿名效果

此时处理函数收到的`event`来自于私聊 B，但`device`对应群聊 A，`event.user_id` = B 的 id，`device.id` = A 的 id

## app

所有插件`app`默认状态都是`idle`

`app`可以通过`set_state`方法切换到不同的状态`state`，由于一个`app`会服务多个`device`，因此除了要设置的下一个状态外，还需要传递当前的`device`对象

`app`在注册触发器`trigger`时可以指定其在某个或某些状态时触发，从而实现同一个命令在不同状态下的不同触发响应，例如#exit

## trigger

`app`可以注册的触发器有四种：消息触发、命令触发、定时触发、监视触发

命令触发`@app.command()`可由形如 #xxx arg1 arg2 的消息触发，xxx 为指定命令或命令组

消息触发`@app.message()`可由形如 xxx arg1 arg2 的触发，如果一个消息形如 #xxx arg1 arg2，但并没有对应匹配的命令触发，ayaka 会将它删除#后视为 xxx arg1 arg2 消息处理

定时触发`@app.everyday()`每日到达设定时间时便会触发一次，ayaka 的扫描周期为 1s（与 heartbeat 周期相同，可修改 cqhttp 中的设置）

监视触发`@app.supervise()`将无条件在任何触发之前，抢先处理 event

# 更新计划

感觉随着 talk.json 的增加，有必要搞个自动化测试了，看看是否存在消息失效问题

一些 talk.json 的词条（例如发送某些图片，甚至发送一些合并转发消息）利用 cqhttp 的数据库取巧了，应该是时候改变了，毕竟 cqhttp 的数据库中大部分是垃圾，需要清理，不然太大了，而且找起来也不方便

# 拆解笔记

## nonebot.internal.adapter

### start_forward、stop_forward、\_forward_ws

比较有意思

估计是用于 web 后端服务器使用，可以通过该方法，利用浏览器监控 bot

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

### \_handle_api_result

检查超时情况，例如消息发送超时

## TYPE_CHECKING

估计是用来解决循环引用的一种方法，后面函数参数约束可以写"ClassName"

## 各种接口 driver、adapter 跳来跳去

估计也是为了解决循环引用，但是显然这种方法很傻逼，代码可阅读性为 0

## 全部功能模块

> driver - fastapi
>
> 负责实现 ws 通信 setup_websocket_server

> adapter
>
> 负责监听 driver 传来的 ws 请求，创建相应 bot，并连接 bot 和 driver，driver 只关心 ws 的实现，bot 只关心高层的抽象（调用高级函数实现对应功能，获得已经处理好的 event 等）
>
> 原本 adapter 的设计可以允许多个 cqhttp 客户端向服务器端发起请求

> **event.py**
>
> 包含各种各样的事件，将 json 转换为对应的事件（事件内同时包含消息

> message
>
> 实现一个可以容纳多种类型内容的消息容器

bot 提供多样的高级函数，例如对群组发送消息、获取好友列表信息等；得益于 cqhttp 良好的接口定义，它们都基于 call_api 实现，且见名知义

> **logger.py**
>
> 基于 Colorama 自行实现一套漂亮的日志代码

assignment 处理消息，分发给各个插件

plugin 提供插件抽象

## 循环引用 1.0

已知的几组循环有：

1. assignment <-> bot <-> adapter 相互引用

bot 的高级方法依赖于 adapter 的 api 实现，adapter 需要将 ws 收到的数据转化为 event 并传递给 bot

bot 需要将 event 和自身传递给 assignment，assignment 需要调用 bot 的方法实现功能

2. event <-> bot 一些 event 的方法需要调用 bot（加好友请求）

3. template <-> message

driver 只负责提供 ws 通信方法，因此和 adapter 没有循环引用关系

logger、model、utils 都是基础方法/类库

## 循环引用 1.1

assignment <-> bot <-> adapter 相互引用 相互引用 已解套

通过更高层的 ws 流程控制解开 即 listen.py

ayaka.\_\_init\_\_ -> listen -> bot, adapter, assignment

主要方式是，listen 主动调用 bot、adapter，将下一步的调用方法（位于 listen）告知这些模块，这些模块将在恰当时候自动调用该方法，从而从 adapter、bot 无引用的跳转到 listen
