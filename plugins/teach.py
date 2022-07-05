from math import ceil
from ayaka.lazy import *
from ayaka.div import pack_message_nodes, div_cmd_arg, div_arg
from kiana.check import check_integer
from plugins.talk import corpus

cache = Cache()

app = AyakaApp(name='teach')
app.help = {
    "idle": "教机器人说话",
    'menu': "[add] 添加\n[change] 修改",
    'add_1': "[<文字>] 输入问题",
    'add_2': "[<文字>] 输入回答",
    "change_1": "[<文字>] 输入问题以检索",
    "change_2": "[<数字>] 输入数字以选择要修改的条目",
    "change_3": "[q] 修改问题\n[a] 修改回答\n[del] 删除本条",
    "change_4": "[<文字>] 输入更新后的问题",
    "change_5": "[<文字>] 输入更新后的回答"
}


async def set_state_and_send_help(bot: Bot, event: GroupMessageEvent, device: AyakaDevice, state: str):
    app.set_state(device, state)
    await bot.send(event, app.help[state])


async def add_q_and_a(bot: Bot, event: GroupMessageEvent, device: AyakaDevice, q: str, a: str):
    corpus.teach(q, a)
    await bot.send(event, f"问：{q}\n答：{a}")
    await set_state_and_send_help(bot, event, device, "menu")


async def send_group_forward_safe(bot: Bot, event: GroupMessageEvent, items: list):
    # 自动分割长消息组（不可超过100条）
    list_max = 80
    div_num = ceil(len(items) / list_max)
    divs = [items[i * list_max: (i+1) * list_max] for i in range(div_num)]
    for div in divs:
        nodes = pack_message_nodes(div)
        await bot.call_api('send_group_forward_msg', group_id=event.group_id, messages=nodes)


async def change_q_a(bot: Bot, event: GroupMessageEvent, device: AyakaDevice, q_flag: bool):
    msg = str(event.message).strip()

    if not msg:
        await bot.send(event, '输入为空')
        return

    id = cache.get_cache(device.id, 'id')
    if q_flag:
        corpus.set_item(id, q=msg)
    else:
        corpus.set_item(id, a=msg)

    await bot.send(event, '修改成功')
    await set_state_and_send_help(bot, event, device, 'menu')


def corpus_data_2_str(data: dict):
    ans = f"问题：{data['key']}\n回答："
    v = data['value']
    if type(v) is list:
        ans += '（具有多个）\n'
        ans += '\n'.join(v)
    else:
        ans += v
    return ans


async def find_questions(bot: Bot, event: GroupMessageEvent, device: AyakaDevice, key: str):
    if not key:
        await bot.send(event, "没有输入参数")
        return

    data = corpus.get_items(key)

    if not data:
        await bot.send(event, "没有找到相关问题")
        return

    ans_list = []
    for i in range(len(data)):
        ans = f'[{i}]\n' + corpus_data_2_str(data[i])
        ans_list.append(ans)

    await send_group_forward_safe(bot, event, ans_list)

    id_list = [d["id"] for d in data]
    cache.set_cache([device.id, 'id_list'], id_list)
    await set_state_and_send_help(bot, event, device, "change_2")


# 指令部分
@app.command(['teach', '教学'])
async def start(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    f, info = device.start_app(app.name)
    await bot.send(event, info)
    if f:
        await set_state_and_send_help(bot, event, device, "menu")


@app.command(['help', '帮助'], ['menu', 'add_1', 'add_2', 'change_1', 'change_2', 'change_3', 'change_4', 'change_5'])
async def help(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    state = app.get_state(device)
    await bot.send(event, app.help[state])


# 添加
@app.command(['add', '添加'], 'menu')
async def add_0(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    cmd, args, arg = div_cmd_arg(['add', '添加'], event.message)

    # 没有变量，正常进入下一个状态
    if len(args) == 0:
        await set_state_and_send_help(bot, event, device, "add_1")
        return

    if len(args) == 1:
        cache.set_cache([device.id, 'question'],  args[0])
        await set_state_and_send_help(bot, event, device, "add_2")
        return

    if len(args) >= 2:
        question = args[0]
        answer = args[1]
        await add_q_and_a(bot, event, device, question, answer)


# 输入问题
@app.message('add_1')
async def add_1(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    args = div_arg(event.message)
    if not args:
        await bot.send(event, '输入为空')
        return

    cache.set_cache([device.id, 'question'], args[0])
    await set_state_and_send_help(bot, event, device, "add_2")
    return True


# 输入回答
@app.message('add_2')
async def add_2(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    args = div_arg(event.message)
    if not args:
        await bot.send(event, '输入为空')
        return

    question = cache.get_cache(device.id, 'question')
    answer = args[0]
    await add_q_and_a(bot, event, device, question, answer)
    return True


# 退出添加
@app.command(['exit', '退出'], ['add_1', 'add_2'])
async def exit_add(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    await bot.send(event, f"已取消添加")
    await set_state_and_send_help(bot, event, device, "menu")


# 彻底退出
@app.command(['exit', '退出'], 'menu')
async def exit_menu(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    f, info = device.stop_app()
    await bot.send(event, info)
    if f:
        app.set_state(device, "idle")


# 修改
@app.command(['change', '修改'], 'menu')
async def change_menu(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    if event.message_type != 'group':
        await bot.send(event, "该功能仅支持群聊")
        return

    cmd, args, arg = div_cmd_arg(['change', '修改'], event.message)

    # 没有变量，正常进入下一个状态
    if len(args) == 0:
        await set_state_and_send_help(bot, event, device, "change_1")
        return

    if len(args) >= 1:
        await find_questions(bot, event, device, args[0])


# 输入查询词
@app.message('change_1')
async def handle(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    msg = str(event.message).strip()
    await find_questions(bot, event, device, msg)
    return True

# 选择修改条目


@app.message('change_2')
async def handle(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    msg = str(event.message)
    if not msg:
        await bot.send(event, '输入为空')
        return

    if not check_integer(msg):
        await bot.send(event, '请输入纯数字')
        return

    i = int(msg)
    id_list = cache.get_cache(device.id, 'id_list')

    if i >= len(id_list) or i < 0:
        await bot.send(event, '超出范围')
        return

    id = id_list[i]

    data = corpus.get_item(id)
    ans = corpus_data_2_str(data)
    await bot.send(event, ans)

    cache.set_cache([device.id, 'id'], id)
    await set_state_and_send_help(bot, event, device, "change_3")
    return True


# 选择修改问题
@app.command('q', 'change_3')
async def handle(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    await set_state_and_send_help(bot, event, device, "change_4")


# 选择修改回答
@app.command('a', 'change_3')
async def handle(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    await set_state_and_send_help(bot, event, device, "change_5")


# 选择删除条目
@app.command('del', 'change_3')
async def handle(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    id = cache.get_cache(device.id, 'id')
    corpus.del_item(id)

    await bot.send(event, "成功删除")
    await set_state_and_send_help(bot, event, device, "menu")


# 输入新问题
@app.message('change_4')
async def handle(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    await change_q_a(bot, event, device, True)
    return True


# 输入新回答
@app.message('change_5')
async def handle(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    await change_q_a(bot, event, device, False)
    return True


# 退出修改
@app.command(['exit', '退出'], ['change_1', 'change_2', 'change_3', 'change_4', 'change_5'])
async def exit_change(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    await bot.send(event, f"已取消修改")
    await set_state_and_send_help(bot, event, device, "menu")
