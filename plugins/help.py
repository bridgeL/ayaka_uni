from ayaka.lazy import *
from ayaka.div import div_cmd_arg
from ayaka.plugin.app import help_dict


app = AyakaApp(name='help')
app.help =  {
    "idle": "帮助文档",
}


def get_help(key):
    if not key:
        names = list(help_dict.keys())
        names.insert(0, '已安装插件')
        return '\n'.join(names)

    if key not in help_dict:
        return "没找到相关帮助"

    name = key
    help = help_dict[key]['idle']
    return f"插件名: {name}\n{help}"


@app.command(['help', '帮助'])
async def help(bot: Bot, event: GroupMessageEvent, device):
    cmd, args, arg = div_cmd_arg(['help', '帮助'], event.message)
    ans = get_help(arg)
    await bot.send(event, ans)
