import re
from asyncio import sleep as a_sleep

from ayaka.lazy import *
from kiana.check import check_integer

from .my_poetry import Poetry

cache = Cache()
poetry = Poetry()
app = AyakaApp(name='poetry')
app.help = {
    "idle": "诗歌",
    "menu": "[#add] 添加一首诗\n[#list] 诗歌列表\n[<诗名>] 从上次中断处念诗\n[<诗名> <数字>] 从指定行开始念诗",
    "add_1": "[<文字>] 输入诗歌名称",
    "add_2": "[<文字>] 输入诗歌内容，可解析多行文本 或 合并转发消息",
    "speak": "[#exit] 退出"
}


async def sleep(line: str):
    t = 0.2 * len(line)
    t = 0.4 if t < 0.4 else t

    s = 5
    if t > s:
        t = (t - s) / 4 + s

    await a_sleep(t)


async def set_state_and_send_help(bot: Bot, event: GroupMessageEvent, device: AyakaDevice, state: str):
    app.set_state(device, state)
    await bot.send(event, app.help[state])


async def speak(bot: Bot, event: GroupMessageEvent, device: AyakaDevice, args):
    title = args[0].lstrip('#')

    # 查询诗歌是否存在
    item = poetry.get_poetry(title)
    if item is None:
        await bot.send(event, f'没有收录诗歌《{title}》')
        return

    if len(args) >= 2:
        last_line_num = args[1]
        if not check_integer(last_line_num):
            await bot.send(event, f'请输入正确数字')
            return
        last_line_num = int(last_line_num)

    else:
        # 默认从上次位置继续
        if 'last_line_num' in item:
            last_line_num = item['last_line_num']
        else:
            last_line_num = 0
            item['last_line_num'] = 0

    time_s = item['time_s']
    lines = item['content']

    if last_line_num >= 0:
        await bot.send(event, f"从第{last_line_num}行开始")
    else:
        await bot.send(event, f"从倒数第{-last_line_num}行开始")
        last_line_num += len(lines)

    if last_line_num >= len(lines) or last_line_num < 0:
        await bot.send(event, f'超出范围')
        return

    # 修改状态为speak
    app.set_state(device, 'speak')

    await bot.send(event, f"《{title}》\n添加时间：{time_s}")

    last_line = title

    # 循环朗读
    for i in range(last_line_num, len(lines)):
        line = lines[i]
        await sleep(last_line)

        # 监测state
        if app.get_state(device) != 'speak':
            break

        line = line.rstrip(',.，。、;；')
        msg = Message(line)
        await bot.send(event, msg)

        last_line = msg.extract_plain_text()

    if i == len(lines) - 1:
        i = 0
    poetry.set_last_line_num(title, i)
    await set_state_and_send_help(bot, event, device, "menu")

    return True


async def add_title(bot: Bot, event: GroupMessageEvent, device: AyakaDevice, msg: str):
    if not msg:
        await bot.send(event, '不可输入为空')
        return

    cache.set_cache(device.id, data=msg)
    await bot.send(event, f"诗歌名 {msg}")
    await set_state_and_send_help(bot, event, device, "add_2")


# 启动
@app.command(['poetry', '诗歌'])
async def start(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    f, info = device.start_app(app.name)
    await bot.send(event, info)
    if f:
        # 分离参数
        cmd, args, arg = div_cmd_arg(['poetry', '诗歌'], event.message)
        if args:
            app.set_state(device, 'menu')
            await speak(bot, event, device, args)
        else:
            await set_state_and_send_help(bot, event, device, "menu")


# 彻底退出
@app.command(['exit', '退出'], 'menu')
async def exit_menu(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    f, info = device.stop_app()
    await bot.send(event, info)
    if f:
        app.set_state(device, "idle")


# 添加
@app.command(['add', '添加'], 'menu')
async def add_0(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    cmd, args, arg = div_cmd_arg(['add', '添加'], event.message)

    # 没有变量，正常进入下一个状态
    if len(args) == 0:
        await set_state_and_send_help(bot, event, device, "add_1")
        return

    if len(args) >= 1:
        await add_title(bot, event, device, args[0])


@app.message('add_1')
async def add_1(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    msg = event.get_plaintext().strip().lstrip("#")
    await add_title(bot, event, device, msg)
    return True


@app.message('add_2')
async def add_2(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    # 解析多行文本 或 合并转发消息
    if event.message[0].type == 'forward':
        id = event.message[0].data['id']
        res_json = await bot.call_api('get_forward_msg', message_id=id)

        msgs = res_json['messages']

        # 得到多行数组
        lines = [msg['content'].rstrip('\r\n') for msg in msgs]
    else:
        # 得到多行数组
        lines = str(event.message).replace('\r\n', '\n').split('\n')

    if not ''.join(lines):
        await bot.send(event, '不可输入为空')
        return

    # 提取纯净文字
    def get_pure_line(line: str):
        pure_line = re.sub(r'(?<=[^,.，。、；;])[,.，。、；;]$', '', line)
        return pure_line

    lines = [get_pure_line(line) for line in lines]

    # 排除空行
    lines = [line for line in lines if line]

    title = cache.get_cache(device.id)
    poetry.set_poetry(title, lines)

    await bot.send(event, f"成功保存诗歌《{title}》")
    ans = '\n'.join(lines[:10])
    await bot.send(event, ans[:200])

    await set_state_and_send_help(bot, event, device, "menu")
    return True


# 退出添加
@app.command(['exit', '退出'], ['add_1', 'add_2'])
async def exit_add(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    await bot.send(event, "已取消添加")
    await set_state_and_send_help(bot, event, device, "menu")


# 帮助
@app.command(['help', '帮助'], ['menu', 'add_1', 'add_2', 'speak'])
async def help(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    state = app.get_state(device)
    await bot.send(event, app.help[state])


# 查看列表
@app.command(['list', '列表'], 'menu')
async def list_show(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    await bot.send(event, "已收录以下诗歌")
    await bot.send(event, poetry.print_list())


# 朗读
@app.message('menu')
async def menu_speak(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    # 分离参数
    args = div_arg(event.message)
    await speak(bot, event, device, args)
    return True


# 退出朗读
@app.command(['exit', '退出'], ['speak'])
async def exit_speak(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    await bot.send(event, "已终止朗读")
    app.set_state(device, "menu")
