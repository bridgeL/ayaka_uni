from random import randint
from ayaka.lazy import *
from ayaka.div import div_cmd_arg

app = AyakaApp(name="yydz")
app.help = {
    "idle": "选择困难了吗？让顶针来帮你吧"
}

# 仅当idle状态时生效
@app.command(["yydz", "一眼丁真"])
async def handle(bot: Bot, event:GroupMessageEvent, device: AyakaDevice):
    cmd, args, arg = div_cmd_arg(["yydz", "一眼丁真"], event.message)
    if not args:
        await bot.send(event, "一眼丁真，鉴定为啥也没输入")
    elif len(args) == 1:
        await bot.send(event, "一眼丁真，鉴定为没得选")
    else:
        ans = args[randint(0,len(args)-1)]
        await bot.send(event, f"一眼丁真，鉴定为 {ans}")



