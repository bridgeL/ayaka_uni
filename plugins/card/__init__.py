"""
    解析一些小程序的分享卡片
"""

import json
from typing import List, Optional
from ayaka.div import div_cmd_arg
from ayaka.lazy import *
from kiana.file import create_file, _save_dict

from .model import BaseJson

app = AyakaApp(name="card")
app.help = {
    "idle": "记录并解析卡片内容\n[#解析卡片 <数字>] 解析最近的第n个卡片, 1 <= n <= 5"
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

            # 分析
            data = BaseJson(**data)
            last: Optional[List[BaseJson]] = cache.get_cache(device.id, 'last')

            if last is None:
                last: List[BaseJson] = []

            for i in last:
                print(i.prompt)
                print(i.meta_val.urls)

            last.append(data)
            cache.set_cache(device.id, 'last', data=last[-5:])


@app.command(["解析卡片", "card", "解析", "卡片"])
async def handle(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    cmd, args, arg = div_cmd_arg(["解析卡片", "card", "解析", "卡片"], event.message)

    i = 1
    if args:
        try:
            i = int(args[0])
        except:
            pass
        else:
            if i > 5:
                await bot.send(event, "最多追踪解析最近的第5个卡片")
                return
            if i < 1:
                i = 1

    last: Optional[List[BaseJson]] = cache.get_cache(device.id, 'last')

    if last is None:
        last: List[BaseJson] = []

    try:
        data = last[-i]
    except:
        await bot.send(event, "卡片过久，无法解析")
    else:
        items = []

        items.append(f"[小程序名称] {data.app}")
        items.append(f"[卡片创建时间] {data.ctime_s}")
        items.append(f"[卡片描述] {data.desc}")
        items.append(f"[卡片提示] {data.prompt}")
        items.append(f"[卡片元内容描述] {data.meta_val.desc}")
        items.append(f"[卡片元内容来源] {data.meta_val.tag}")
        items.append(f"[卡片元内容标题] {data.meta_val.title}")
        s = "\n\n".join(data.meta_val.urls)
        items.append(f"[卡片链接嗅探]\n{s}")

        await bot.send_group_forward_msg(event.group_id, items)
