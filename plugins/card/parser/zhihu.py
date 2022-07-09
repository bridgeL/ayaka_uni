
from math import ceil
import re
from typing import List
from urllib.parse import unquote
from bs4 import BeautifulSoup
from ayaka.lazy import *
from ..model import BaseJson, register_func
from spider import Spider

async def handle(bot: Bot, event: GroupMessageEvent, data:BaseJson):
    image_url = data.meta.raw_data['preview']
    await bot.send(event, Message(MessageSegment.image(image_url)))

    if 'qqdocurl' in data.meta.raw_data:
        url = data.meta.raw_data['qqdocurl']
    else:
        url = data.meta.raw_data['jumpUrl']

    spider_data = Spider(url).get()
    content:BeautifulSoup = spider_data.html_data.select("#root > div > main > div > div > div.Question-main > div.ListShortcut > div > div.Card.AnswerCard.css-0 > div > div > div > div.RichContent.RichContent--unescapable > div.RichContent-inner > span")[0]

    # 纯文字
    text:str = content.getText("\n",strip=True)
    items = text.split("\n")
    if items:
        await bot.send_group_forward_msg(event.group_id, items)

    # 嗅探所有链接
    anchors:List[BeautifulSoup] = content.find_all("a")
    items = []
    for anchor in anchors:
        url = anchor['href']
        url = re.sub(r"^https://link.zhihu.com/\?target=","",url)
        url = unquote(url)
        name = anchor.getText(strip=True)
        items.append(f"{name}\n{url}")
    if items:
        await bot.send_group_forward_msg(event.group_id, items)

register_func("知乎", handle)