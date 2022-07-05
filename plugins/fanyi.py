from ayaka.lazy import *
from ayaka.div import div_cmd_arg
import requests

app = AyakaApp(name='fanyi')
app.help = {
    "idle": "[fy <参数>] 缩写翻译",
}

@app.command(['fanyi','fy','翻译'])
async def fanyi(bot:Bot, event:GroupMessageEvent, device:AyakaDevice):
    cmd, args, arg = div_cmd_arg(['fanyi','fy','翻译'], event.message)
    if arg:
        response = requests.post(
            url='https://lab.magiconch.com/api/nbnhhsh/guess',
            data={'text': arg }
        )
        result = response.json()
        if result:
            result = result[0]
            if 'trans' in result:
                ans = ''
                for t in result["trans"]:
                    ans += t + ' '
                await bot.send(event,'[翻译]{0}'.format(ans))
            if 'inputting' in result:
                await bot.send(event,'可能是{0}'.format(result["inputting"]))
        else:
            await bot.send(event,'请求的API不稳定，请稍后重试')
    else:
        await bot.send(event,'没有输入参数')

