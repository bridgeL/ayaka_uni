from ayaka.lazy import *
from kiana.time import get_date_s
from plugins.bag import add_money, get_name

app = AyakaApp(name='checkin')
app.help = "签到"


@app.command(['checkin', '签到'])
async def checkin(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    name = get_name(event)

    ST = Storage(event.group_id, 'members', event.user_id, 'checkin')
    date = get_date_s()
    if date == ST.get():
        await bot.send(event, f"[{name}] 今天已经签到过了")
        return

    ST.set(date)

    money = add_money(200000, event=event)
    await bot.send(event, f"[{name}] 签到成功，系统奖励 200000金")
    await bot.send(event, f"[{name}] 当前拥有 {money}金")
