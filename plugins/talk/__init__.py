from ayaka.lazy import *
from .corpus import Corpus

corpus = Corpus('data/talk.json')

app = AyakaApp(name='talk')
app.help = "命令式傻瓜聊天机器人"


@app.message()
async def talk(bot: Bot, event: GroupMessageEvent, device):
    msg = str(event.message)
    ans = corpus.search(msg, True)
    if ans:
        await bot.send(event, Message(ans))
        return True
    return False
