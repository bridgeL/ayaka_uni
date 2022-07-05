from ayaka.lazy import *
from ayaka.div import div_cmd_arg
from kiana.file import load_json

mars_data = load_json('data/mars.json')
charPYStr:str = mars_data['charPYStr']
ftPYStr:str = mars_data['ftPYStr']

def judge(cc):
    mars_yes = 0
    mars_no = 0
    for c in cc:
        if c in charPYStr:
            mars_no += 1
        elif c in ftPYStr:
            mars_yes += 1
    return mars_yes > mars_no

def mars_encode(cc):
    str = ''
    for c in cc:
        i = charPYStr.find(c)
        if i >= 0:
            str += ftPYStr[i]
        else:
            str += c
    return str

def mars_decode(cc):
    str = ''
    for c in cc:
        i = ftPYStr.find(c)
        if i >= 0:
            str += charPYStr[i]
        else:
            str += c
    return str

app = AyakaApp(name='mars')
app.help = {
    "idle": "火星文转换器",
}

@app.command(['mars','火星文'])
async def mars(bot:Bot, event:GroupMessageEvent, device:AyakaDevice):
    cmd, args, arg = div_cmd_arg(['mars','火星文'], event.message)
    if arg:
        if judge(arg):
            ans = mars_decode(arg)
        else:
            ans = mars_encode(arg)
        await bot.send(event,ans)
    else:
        await bot.send(event, app.help['idle'])
