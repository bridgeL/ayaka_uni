from ayaka.lazy import *
from ayaka.div import div_cmd_arg


app = AyakaApp(name='around')
app.help = {
    "idle": "环绕字，例如：\n#81 ab C\n\n生成\nababab\nabCab\nababab",
}


@app.command(['around', '81', '环绕', '环绕字'])
async def around(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    cmd, args, arg = div_cmd_arg(['around', '81', '环绕', '环绕字'], event.message)
    if args:
        a = args[0]
        try:
            b = args[1]
        except:
            b = a[1:]
            a = a[:1]
        ans = f"{a*3}\n{a}{b}{a}\n{a*3}"
        await bot.send(event, ans)
    else:
        await bot.send(event, '没有输入参数')
