import os
import sys
import requests
from ayaka.lazy import *
from pydantic import BaseModel
from spider import Spider

app = AyakaApp(name="setu")
app.help = {
    "idle": '来张涩图\n[#setu] 可以色色'
}

# 提供header的傀儡罢了
header_provider = Spider("")


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
            f"{self.title}",
            f"[作者] {self.author}",
            f"[地址] {self.url}"
        ])
        return ans


proxy = 'http://127.0.0.1:7890'
proxies = {'http': proxy, 'https': proxy}

dirpath = "data/setu"
if not os.path.exists(dirpath):
    os.makedirs(dirpath)


@app.command(['setu', '涩图', '色图', '瑟图'])
async def handle(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    local = sys.platform == 'win32'
    print(local)

    try:
        # 获取url
        if local:
            res = requests.get('https://api.lolicon.app/setu/v2', proxies=proxies)
        else:
            res = requests.get('https://api.lolicon.app/setu/v2')

        res = res.json()
        res = res["data"][0]
    except:
        await bot.send(event, 'setu 未获取到图片地址')
        return
    else:
        # 提取感兴趣的属性
        data = SetuData(**res)
        ans = data.get_info()
        await bot.send(event, ans)

    try:
        headers = header_provider.get_headers()
        if local:
            res = requests.get(data.url, headers=headers, stream=True, proxies=proxies)
        else:
            res = requests.get(data.url, headers=headers, stream=True)

        res = res.content
        open(f'{dirpath}/{data.name}', 'wb').write(res)
        await bot.send(event, Message(MessageSegment.image(res)))
    except:
        await bot.send(event, 'setu 发送图片失败')
        return
