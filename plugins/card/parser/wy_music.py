from ayaka.lazy import *
from ..model import BaseJson, register_func, is_image_url

async def handle(bot: Bot, event: GroupMessageEvent, data:BaseJson):
    for url in data.meta.urls:
        if "music.163.com/song/media/outer" in url:
            await bot.send(event, url)
        if is_image_url(url):
            await bot.send(event, Message(MessageSegment.image(url)))

register_func("网易云音乐", handle)