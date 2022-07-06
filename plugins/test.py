from ayaka.lazy import *
from ayaka.div import div_cmd_arg

app = AyakaApp(name="test")
app.help = {
    "idle": "啊",
    "test": "复读机"
}


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
    cmd, args, arg = div_cmd_arg(["复读", "repeat"], event.message)

    # 复读第二个参数
    if len(args) >= 2:
        await bot.send(event, args[1])
    else:
        await bot.send(event, "参数不够多")

    # arg为 排除了命令外的所有参数 的 字符串之和
