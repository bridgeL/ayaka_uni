import re
from ayaka.div import div_cmd_arg
from ayaka.lazy import *


app = AyakaApp(name='bag')
app.help = {
    "idle": "背包",
}


def get_name(event: GroupMessageEvent):
    name = event.sender.card
    if not name:
        name = event.sender.nickname
    return name


def get_money(gid=None, uid=None, event: GroupMessageEvent = None):
    if gid == None:
        gid = event.group_id
        uid = event.user_id
    MONEY_ST = Storage(gid, 'members', uid, 'money')
    return MONEY_ST.get(default=100)


def add_money(diff: int, gid=None, uid=None, event: GroupMessageEvent = None):
    if gid == None:
        gid = event.group_id
        uid = event.user_id
    MONEY_ST = Storage(gid, 'members', uid, 'money')
    money = MONEY_ST.get(default=100) + diff
    MONEY_ST.set(money)
    return money

async def get_uid_name(bot:Bot, event:GroupMessageEvent, arg:str):
    r = re.search(r"\[CQ:at,qq=(?P<uid>\d+)\]", arg)
    if r:
        uid = int(r.group('uid'))
        data = await bot.get_group_member_info(group_id=event.group_id, user_id=uid)
        name = data['card'] if data['card'] else data['nickname']
        return uid, name

    r = re.search(r"@(?P<name>\w+)", arg)
    if r:
        uid = 0
        name = r.group('name')
        data = await bot.get_group_member_list(group_id=event.group_id)
        for d in data:
            if d['card'] == name or d['nickname'] == name:
                uid = d['user_id']
        return uid, name

    return 0, ""


@app.command(['bag', '背包'])
async def bag(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    cmd, args, arg = div_cmd_arg(['bag', '背包'], event.message)
    if len(args) >= 1:
        uid, name = await get_uid_name(bot, event, args[0])
    else:
        uid = event.user_id
        name = get_name(event)

    if not uid:
        await bot.send(event, "查无此人")
        return

    money = get_money(gid=event.group_id, uid=uid)

    ans = f"[{name}] 当前有 {money}金"
    await bot.send(event, ans)
