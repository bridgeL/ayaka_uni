from ayaka.lazy import *
from kiana.file import load_json
from random import randint
import re
from pypinyin import lazy_pinyin

# 语料库
words = load_json('data/genshin_dragon/bin.json')
search_bin = load_json('data/genshin_dragon/search.json')

not_zh = re.compile(r'[^\u4e00-\u9fa5]*')


app = AyakaApp(name="genshin_dragon")
app.help = "原神接龙，关键词中了就行"


@app.message()
async def handle(bot: Bot, event: GroupMessageEvent, device):
    msg = event.get_plaintext().strip()

    # 删除所有非汉字
    msg = not_zh.sub('', msg)

    if not msg:
        return

    if msg not in words:
        return

    py = lazy_pinyin(msg[-1])[0]
    if py not in search_bin:
        return

    ans_list = search_bin[py]
    if ans_list:
        ans = ans_list[randint(0, len(ans_list)-1)]
        await bot.send(event, ans)
        return True
