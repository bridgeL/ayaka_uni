from random import randint
from ayaka.lazy import *

app = AyakaApp(name="yydz")
app.help = "选择困难了吗？让丁真来帮你吧\n[#yydz]"


@app.command(["yydz", "一眼丁真"])
async def handle(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    cmd, args, arg = div_cmd_arg(["yydz", "一眼丁真"], event.message)
    if not args:
        await bot.send(event, "一眼丁真，鉴定为 啥也没输入")
    elif len(args) == 1:
        await bot.send(event, "一眼丁真，鉴定为 没得选")
    else:
        i = randint(0, len(args)*3)
        if i == 0:
            ans = ["我全都要", "为定鉴，真丁眼一", "".join(args)][randint(0, 2)]
        else:
            ans = args[i % len(args)]
        await bot.send(event, f"一眼丁真，鉴定为 {ans}")
