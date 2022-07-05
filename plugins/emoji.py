from math import ceil
from ayaka.lazy import *
from ayaka.div import div_cmd_arg, pack_message_nodes
from kiana.file import load_json


emojiBin = load_json('data/emoji.json')

app = AyakaApp(name='emoji')
app.help = {
    "idle": "[#e <参数>] 简单查询emoji\n[#emoji <参数>] 详细查询emoji",
}

@app.command(['e','emoji'])
async def emoji(bot:Bot, event:GroupMessageEvent, device:AyakaDevice):
    cmd, args, arg = div_cmd_arg(['e','emoji'], event.message)
    if not arg:
        await bot.send(event, app.help['idle'])
        return

    def relate(tags, keys:list):
        tag_all = ' '.join(tags)
        for key in keys:
            if tag_all.find(key) < 0:
                return False
        return True

    es = [e for e in emojiBin if relate(emojiBin[e], args)]

    if not es:
        await bot.send(event, '没有相关结果')
        return

    if cmd == 'emoji':
        items = []
        for e in es:
            items.append(f"{e} 标签\n" + "\n".join(emojiBin[e]))
        es = items

    await send_group_forward_safe(bot, event, es)


async def send_group_forward_safe(bot:Bot, event:GroupMessageEvent, items:list):
    # 自动分割长消息组（不可超过100条）
    list_max = 80
    div_num = ceil(len(items) / list_max)
    divs = [ items[ i * list_max : (i+1) * list_max ] for i in range(div_num) ]
    for div in divs:
        nodes = pack_message_nodes(div)
        await bot.call_api('send_group_forward_msg', group_id=event.group_id, messages=nodes)

