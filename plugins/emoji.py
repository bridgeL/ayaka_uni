from ayaka.lazy import *
from kiana.file import load_json


emojiBin = load_json('data/emoji.json')

app = AyakaApp(name='emoji')
app.help = "[#e <参数>] 简单查询emoji\n[#emoji <参数>] 详细查询emoji"


@app.command(['e', 'emoji'])
async def emoji(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    cmd, args, arg = div_cmd_arg(['e', 'emoji'], event.message)
    if not arg:
        await bot.send(event, app.help['idle'])
        return

    def relate(tags, keys: list):
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

    await bot.send_group_forward_msg(event.group_id, es)



