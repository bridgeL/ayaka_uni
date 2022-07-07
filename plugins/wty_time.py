from ayaka.lazy import *
from kiana.time import get_time_i_pure, get_time_s_pure


app = AyakaApp(name='wty_time')
app.help = "wty现在几点了\n[#wt]"


@app.command(['wty_time', 'wty现在几点了', 'wt'])
async def test(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    time_i = get_time_i_pure() + 3600*11
    time_s = get_time_s_pure(time_i)
    await bot.send(event, time_s)
