from kiana.file import create_file
from kiana.time import get_date_s_hyphen, get_time_s
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, unescape
from nonebot.message import event_preprocessor

async def record(group:bool, id:int, name, uid, message):
    date_s = get_date_s_hyphen()

    head = "group" if group else "private"
    path = create_file(f"{date_s}.log", f"data/record/{head}/{id}")

    message = unescape(str(message))
    text = f'[{get_time_s()}] {name}({uid}) 说: {message}'
    with open(path, 'a+', encoding='utf8') as f:
        f.write(f'{text}\n')

# 记录ayaka bot的发送
@Bot.on_called_api
async def handle_api_call(bot: Bot, exception, api: str, data, result):
    print('handle_api_call result',result)

    if api == 'send_msg':
        group = data['message_type'] == 'group'
        id = data['group_id'] if group else data['user_id']
        msg = data['message']
        await record(group, id, 'Ayaka Bot', 2317709898, msg)

    elif api == 'send_group_forward_msg':
        group = True
        id = data['group_id']
        ms = [m['data']['content'] for m in data['messages']]
        msg = '\n'.join(ms)
        await record(group, id, 'Ayaka Bot', 2317709898, msg)

# 记录ayaka bot的接收
@event_preprocessor
async def handle(bot:Bot,event:GroupMessageEvent):
    group = event.message_type == 'group'
    name = event.sender.nickname

    if group and event.sender.card:
        name = event.sender.card

    id = event.group_id if group else event.user_id
    uid = event.user_id

    ms = event.message[0]

    if ms.type == 'forward':
        fid = ms.data['id']
        res_json = await bot.call_api(api='get_forward_msg', message_id=fid)

        items = [node['content'] for node in res_json['messages']]
        msg = '\n'.join(items)
    else:
        msg = str(event.message)

    await record(group, id, name, uid, msg)



