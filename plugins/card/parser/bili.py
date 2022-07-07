import re
from typing import List
from bs4 import BeautifulSoup
from ayaka.lazy import *
from ..model import BaseJson, register_func, is_image_url
from spider import Spider

async def handle(bot: Bot, event: GroupMessageEvent, data:BaseJson):
    for url in data.meta.urls:
        if "https://b23.tv/" in url:
            url = url[:url.find('?')]
            await bot.send(event, url)

            spider_data = Spider(url=url).get()
            head:BeautifulSoup = spider_data.html_data.head
            metas:List[BeautifulSoup] = head.find_all("meta")

            items = []
            for meta in metas:
                try:
                    itemprop = meta["itemprop"]
                    content:str = meta["content"]
                except:
                    continue
                else:
                    if is_image_url(content):
                        item = Message([
                            MessageSegment.text(f"[{itemprop}]\n"),
                            MessageSegment.image(content)
                        ])
                        items.append(item)
                    elif itemprop == "description":
                        r = re.search(
                            r"(?P<desc>.*?)"
                            r"(?=视频播放量)(?P<digital>.*?)"
                            r"(?=视频作者)(?P<author>.*?)"
                            r"(?=相关视频)(?P<relate>.*)", content)
                        if r:
                            detail = r.groupdict()
                            ds = [f"[{key}]\n{detail[key]}" for key in detail]
                            content = "\n\n".join(ds)

                        items.append(f"[{itemprop}]\n{content}")
                    else:
                        items.append(f"[{itemprop}]\n{content}")

            if items:
                await bot.send_group_forward_msg(event.group_id, items)

        if "pubminishare" in url:
            await bot.send(event, Message(MessageSegment.image( "https://" + url)))

register_func("b站视频", handle)