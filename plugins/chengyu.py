from random import randint
import re
from pypinyin import lazy_pinyin
from ayaka.lazy import *
from ayaka.div import div_cmd_arg
from kiana.file import load_json

app = AyakaApp(name="chengyu")
app.help = {
    "idle": "成语接龙（肯定是你输\n[#cy <参数>] 查询成语\n[什么是 <参数>] 查询成语\n[<参数> 是什么] 查询成语"
}

whole_bin: dict = load_json("data/chengyu/bin.json")
chengyu_list = list(whole_bin.keys())

easy_bin: dict = load_json("data/chengyu/easy.json")
hard_bin: dict = load_json("data/chengyu/hard.json")
# 这里应该加个计分功能

@app.message()
async def handle(bot: Bot, event: GroupMessageEvent, device:AyakaDevice):
    msg = event.get_plaintext()

    # 判断是不是在问问题
    r = re.search(
        r'(啥|什么)是\s?(?P<data>[\u4e00-\u9fff]{3,}(.*[\u4e00-\u9fff]{3,})?)', msg)
    if r:
        return await inquire(bot, event, r.group('data'))

    r = re.search(
        r"(?P<data>[\u4e00-\u9fff]{3,}(.*[\u4e00-\u9fff]{3,})?)\s?是(啥|什么)(意思)?", msg)
    if r:
        return await inquire(bot, event, r.group('data'))

    r = re.search(
        r"(?P<data>[\u4e00-\u9fff]{3,}(.*[\u4e00-\u9fff]{3,})?)\s?是成语吗", msg)
    if r:
        return await inquire(bot, event, r.group('data'), must=True)

    # 判断是否需要成语接龙
    # 3字以上的中文，允许包含一个间隔符，例如空格、顿号、逗号、短横线等
    r = re.search(r'[\u4e00-\u9fff]{3,}(.*[\u4e00-\u9fff]{3,})?', msg)
    if not r:
        return

    msg = r.group()
    # 删除标点
    msg = re.sub(r"[^\u4e00-\u9fff]","",msg)

    # 判断是否是成语
    if msg not in chengyu_list:
        return

    # 读取上次
    ST = Storage(device.id, app.name, 'last')
    last = ST.get("")

    from plugins.bag import add_money
    py1 = lazy_pinyin(msg[0])[0]

    if py1 == last:
        add_money(1000, event=event)
        await bot.send(event, f"奖励1000金")
        Storage(device.id, app.name, 'members', event.user_id).inc()

    # 准备下次
    ans = None
    py = lazy_pinyin(msg[-1])[0]
    if py in easy_bin:
        vs = easy_bin[py]

        # 适当放水，可选择回答越少的放水越多
        i = randint(0, len(vs)+1)
        if i < len(vs):
            ans = vs[i]

    if not ans and py in hard_bin:
        vs = hard_bin[py]

        # 适当放水，可选择回答越少的放水越多
        i = randint(0, len(vs)+1)
        if i < len(vs):
            ans = vs[i]

    if ans:
        py2 = lazy_pinyin(ans[-1])[0]
        ans = f"[{py}] {ans} [{py2}]"
        await bot.send(event, ans)

        # 保存
        ST.set(py2)

    else:
        await bot.send(event, "你赢了")

        add_money(10000, event=event)
        ST.set("")
        await bot.send(event, f"奖励10000金")

    return True


# 用户询问
async def inquire(bot: Bot, event: GroupMessageEvent, msg: str, must=False):
    # 删除标点
    msg = re.sub(r"[^\u4e00-\u9fff]","",msg)
    # 判断是否是成语
    if msg not in chengyu_list:
        if not must:
            return
        await bot.send(event, f"[{msg}] 不是成语")
    else:
        pys = lazy_pinyin(msg)
        ans = " ".join(pys)

        val = whole_bin[msg]
        ans = f"[{msg}]\n[{ans}]\n\n{val}"
        await bot.send(event, ans)

    return True


@app.command(["cy","成语"])
async def handle(bot:Bot, event:GroupMessageEvent, device):
    cmd, args, arg = div_cmd_arg(["cy","成语"], event.message)
    if not args:
        await bot.send(event, app.help['idle'])
    else:
        await inquire(bot, event, args[0], must=True)
