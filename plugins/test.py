from ayaka.lazy import *

app = AyakaApp(name='test')
app.help = {"idle": "测试用例"}


@app.command('test')
async def test(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    await bot.send(event, '#test')
