from ayaka.lazy import *
from ayaka.div import div_cmd_arg
from ayaka.plugin.app import help_dict


app = AyakaApp(name='help')
app.help =  {
    "idle": "帮助文档\n[#help <插件名> <状态>] 查询具体插件在指定状态下的帮助",
}


def get_help(key, state=None):
    if not key:
        names = list(help_dict.keys())
        names.insert(0, '已安装插件')
        return '\n'.join(names)

    if key not in help_dict:
        return "没找到相关帮助"

    name = key
    _help:dict = help_dict[key]

    if state in _help:
        return f"插件名: {name}\n状态[{state}]的帮助\n{_help[state]}"
    else:
        ans = f"插件名: {name}\n状态[idle]的帮助\n{_help['idle']}"

        states = [f"[{s}]" for s in _help.keys() if s != 'idle']
        ss = " ".join(states)
        if ss:
            ans += "\n其他状态：{ss}"
        return ans


@app.command(['help', '帮助'])
async def help(bot: Bot, event: GroupMessageEvent, device):
    cmd, args, arg = div_cmd_arg(['help', '帮助'], event.message)

    if len(args) > 1:
        ans = get_help(args[0], args[1])
    else:
        ans = get_help(arg)

    await bot.send(event, ans)
