"""
    解析一些小程序的分享卡片
"""

import json

from ayaka.lazy import *
from ayaka.div import div_cmd_arg
from ayaka.plugin.module import get_all_module_names, import_all_modules
from kiana.file import create_file, _save_dict

from .model import BaseJson, parser_dict

ms = get_all_module_names("plugins/card/parser")
import_all_modules(ms)

app = AyakaApp(name="card")
app.help = {
    "idle": "记录并解析卡片内容\n[#卡片 <模式>] 解析最近的卡片，可以指定解析模式"
}

path = create_file("cards.log", "data")
cache = Cache()


@app.supervise()
async def handle(bot, event: GroupMessageEvent, device: AyakaDevice):
    for ms in event.message:
        if ms.type == 'json':
            data = json.loads(ms.data['data'])

            # 保存
            f = open(path, 'a+', encoding='utf8')
            _save_dict(f, data, 0)
            f.write("\n")
            f.close()

            # 分析并缓存
            data = BaseJson(**data)
            cache.set_cache(device.id, 'last', data=data)


@app.command(["解析卡片", "card", "解析", "卡片"])
async def handle(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    data:BaseJson = cache.get_cache(device.id, 'last')

    if data is None:
        await bot.send(event, "没有捕获到上一张卡片")
        return

    cmd, args, arg = div_cmd_arg(["解析卡片", "card", "解析", "卡片"], event.message)
    if arg:
        print(arg)
        print(parser_dict)
        if arg in parser_dict:
            func = parser_dict[arg]
            await func(bot, event, data)
            return


    items = [
        f"[小程序名称]\n{data.app}",
        f"[卡片创建时间]\n{data.ctime_s}",
        f"[卡片描述]\n{data.desc}",
        f"[卡片提示]\n{data.prompt}",
        f"[卡片元内容描述]\n{data.meta.desc}",
        f"[卡片元内容来源]\n{data.meta.tag}",
        f"[卡片元内容标题]\n{data.meta.title}",
        "[卡片链接嗅探]"
    ]

    items.extend(data.meta.urls)

    await bot.send_group_forward_msg(event.group_id, items)


