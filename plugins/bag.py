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


@app.command(['bag', '背包'])
async def bag(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    await bot.send(event, f"删档测试，现在只能查询自己的背包")

    money = get_money(event=event)
    name = get_name(event=event)

    ans = f"[{name}] 当前有 {money}金"
    await bot.send(event, ans)
