import os
import sys
from ayaka.lazy import *
from pydantic import BaseModel
from spider import Spider

app = AyakaApp(name="setu")
app.help = '来张涩图\n[#setu] 可以色色'


class SetuData(BaseModel):
    pid: int = 0
    title: str = ""
    author: str = ""
    url: str = ""
    name: str = ""

    def __init__(self, **data) -> None:
        url: str = data['urls']['original']
        name = url[url.rfind('/')+1:]
        super().__init__(**data, url=url, name=name)

    def get_info(self):
        ans = "\n".join([
            f"[PID] {self.pid}",
            f"[标题] {self.title}",
            f"[作者] {self.author}",
            f"[地址] {self.url}"
        ])
        return ans


proxy = 'http://127.0.0.1:7890'
api = 'https://api.lolicon.app/setu/v2'

dirpath = "data/setu"
if not os.path.exists(dirpath):
    os.makedirs(dirpath)


@app.command(['setu', '涩图', '色图', '瑟图'])
async def handle(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    local = sys.platform == 'win32'
    if not local:
        print(f"setu正在云端运行")

    try:
        # 获取url
        if local:
            res = Spider(api, proxy=proxy).get()
        else:
            res = Spider(api).get()

        res = res.json_data["data"][0]
    except:
        await bot.send(event, 'setu 未获取到图片地址')
        return
    else:
        # 提取感兴趣的属性
        data = SetuData(**res)
        ans = data.get_info()
        await bot.send(event, ans)

    try:
        if local:
            res = Spider(data.url, stream=True, proxy=proxy).get()
        else:
            res = Spider(data.url, stream=True).get()

        res = res.stream_data
        open(f'{dirpath}/{data.name}', 'wb').write(res)
        await bot.send(event, Message(MessageSegment.image(res)))
    except:
        await bot.send(event, 'setu 太涩了，发不出来(')
        return
