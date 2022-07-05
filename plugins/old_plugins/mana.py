from random import randint
from ayaka.lazy import *
from ayaka.utils import div_cmd_arg
from pydantic import BaseModel
from plugins.bag import add_money, get_name, get_money
from asyncio import sleep

__help__ = {
    "name": "mana",
    "idle": "欢愉、悼亡、深渊、智慧\n[pray <数字>] 祈祷/冥想，至少花费1\n[divine] 占卜，花费1玛娜\n[mana <数字>] 花费金币兑换玛娜；可以反向兑换；0为查询",
}

app = AyakaApp(name='mana', area=AyakaAppArea.GROUP,help=__help__)


def get_mana(event: GroupGroupMessageEvent):
    gid = event.group_id
    uid = event.user_id
    ST = Storage(gid, 'members', uid, 'mana')
    return ST.get(default=100)


def add_mana(diff: int, event: GroupGroupMessageEvent):
    gid = event.group_id
    uid = event.user_id
    ST = Storage(gid, 'members', uid, 'mana')
    mana = ST.get(default=0) + diff
    ST.set(mana)


class ManaGod(BaseModel):
    name = '欢愉'
    power = 1
    cnt = 0
    mana = 0

    def say(self):
        words = {
            '欢愉': ['命途对你报之一笑', '命途轻咬你的耳根', '命途正引诱你堕入其中'],
            '悼亡': ['命途中，亡魂在悲叹', '命途中充斥着悲伤', '命途默然无声地崩解着'],
            '深渊': ['命途静静凝视着你'],
            '智慧': ['命途终极的智慧，令你感到畏惧', '命途看穿了你的企图', '命途对你的愚蠢感到无趣'],
        }

        cs = {
            '欢愉': '♥',
            '悼亡': '♠',
            '深渊': '♣',
            '智慧': '♦',
        }

        # ps = ['魔法师','女祭司','皇后','皇帝','教皇','恋人','战车','力量','隐士','命运之轮','正义','倒吊人','死神']

        rs = words[self.name]
        r = rs[randint(0, len(rs)-1)]
        c = cs[self.name]
        return f"{r} {c} {self.power}"


def get_god(device: AyakaDevice):
    GOD_ST = Storage(device.id, 'mana', 'god')
    god = GOD_ST.get(default=ManaGod().dict())
    return ManaGod(**god)


def set_god(god: ManaGod, device: AyakaDevice):
    GOD_ST = Storage(device.id, 'mana', 'god')
    GOD_ST.set(god.dict())


@app.command(['divine', '占卜'])
async def pray(bot: Bot, event: GroupGroupMessageEvent, device: AyakaDevice):
    name = get_name(event)

    mana = get_mana(event)
    if mana <= 0:
        await bot.send(event, f"[{name}] 只有 [{mana}]玛娜")
        return

    add_mana(-1, event)
    await bot.send(event, f"[{name}] 花费了 1玛娜，聆听星辰的呓语")
    await sleep(1)
    await bot.send(event, f"...")
    await sleep(1)
    await bot.send(event, f"...")
    await sleep(1)

    god = get_god(device)
    await bot.send(event, god.say())


@app.command(['mana', '玛娜'])
async def handle(bot: Bot, event: GroupGroupMessageEvent, device: AyakaDevice):
    cmd, args, arg = div_cmd_arg(['mana', '玛娜'], event.message)
    if not arg:
        await bot.send(event, __help__['idle'])
        return

    try:
        arg = int(arg)
    except:
        arg = 1

    name = get_name(event)

    if arg != 0:
        money = get_money(event=event)
        if money - arg*1000 < 0:
            await bot.send(event, f"[{name}] 只有 [{money}]金")
            return

        mana = get_mana(event)
        if mana + arg < 0:
            await bot.send(event, f"[{name}] 只有 [{mana}]玛娜")
            return

        add_mana(arg, event)
        add_money(-1000*arg, event=event)
        await bot.send(event, f"[{name}] 花费了 {arg*1000}金，获得了 {arg}玛娜")

    money = get_money(event=event)
    mana = get_mana(event)
    await bot.send(event, f"[{name}] 当前有 {money}金，{mana}玛娜")


@app.command(['pray', '祈祷', '冥想'])
async def handle(bot: Bot, event: GroupGroupMessageEvent, device: AyakaDevice):
    cmd, args, arg = div_cmd_arg(['pray', '祈祷', '冥想'], event.message)
    try:
        arg = int(arg)
    except:
        arg = 1
    if arg <= 0:
        arg = 1

    funcs = {
        '欢愉': happy,
        '悼亡': sorrow,
        '深渊': abyss,
        '智慧': wise,
    }

    god = get_god(device)
    old_god_name = god.name

    func = funcs[god.name]
    reward, info = func(god=god, mana=arg)
    reward = int(reward)
    await bot.send(event, info)

    set_god(god, device)
    add_mana(reward - arg, event)

    name = get_name(event)
    mana = get_mana(event)
    await bot.send(event, f"[{name}] 花费了 {arg}玛娜，获得了 {reward}玛娜")
    await bot.send(event, f"[{name}] 当前有 {mana}玛娜")

    if old_god_name != god.name:
        await bot.send(event, "星空在惊惧中震颤，旧的命途陨落，新的命途执掌星空")
        await bot.send(event, god.say())

god_names = ['欢愉', '悼亡', '深渊', '智慧']


def change_god(god_name: str, god: ManaGod):
    god.name = god_name
    god.power = randint(1, 13)
    god.cnt = 0
    god.mana = 0


def happy(god: ManaGod, mana: int):
    power = god.power

    god.mana += mana
    if god.mana >= 8:
        god.power += int(god.mana/8)
        god.mana = 0

    god.cnt += 1
    if god.cnt >= 3:
        god.power += 1
        god.cnt = 0

    if god.power > 13:
        change_god(god_names[randint(0, 3)], god)

    if power <= 3:
        return 0, "命途对你毫无兴趣"
    if power <= 6:
        return 2*(power-3), "命途微微舒展身姿"
    if power <= 10:
        return mana*(1+(power-6)/5), "命途对你兴趣颇丰"
    return mana*(power-9), "命途向你展示了星空的无限隐秘"


def sorrow(god: ManaGod, mana: int):
    power = god.power

    god.mana += mana
    if god.mana >= power:
        god.power += int(god.mana/power)
        god.mana = 0

    god.cnt += 1
    if god.cnt >= 10:
        god.power += 1
        god.cnt = 0

    if god.power > 13:
        change_god(god_names[randint(0, 3)], god)

    if power <= 5:
        return mana, "命途对你悲叹"
    if power <= 10:
        return mana + power - 5, "命途对你怜悯"
    return - power, "命途对你哀悼"


def abyss(god: ManaGod, mana: int):
    power = god.power

    if mana % 3 == 2:
        god.power -= 1
    else:
        god.power += mana % 3

    god.cnt += 1
    if god.cnt >= 12:
        change_god(god_names[randint(0, 3)], god)

    if god.power > 13:
        change_god('欢愉', god)

    if god.power <= 0:
        change_god('悼亡', god)

    if power % 3 == 0 and randint(0, 2):
        return mana * power / 3, "当你理解了命途，你也就成为了命途"
    return mana * (1 - power/6), "命途贪婪的吞噬了一切"


def wise(god: ManaGod, mana: int):
    power = god.power
    reward = int(god.mana / 3)

    god.mana += mana*2 - reward
    if power <= 7:
        god.mana += power*3
    else:
        god.mana += (14 - power)*3

    god.power = int(god.mana / 3) + 1

    god.cnt += 1
    if god.cnt >= 12:
        change_god(god_names[randint(0, 3)], god)

    if god.power > 13 or god.power <= 0:
        change_god(god_names[randint(0, 3)], god)

    return reward, "宇宙的奥秘在命途中盘旋"
