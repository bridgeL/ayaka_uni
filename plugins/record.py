# 926908929
from ayaka.lazy import *
from ayaka.utils.record import record

app = AyakaApp(name="record")


# 记录ayaka bot的接收
@app.supervise()
async def handle(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
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
        items = [
            f"[{node['sender']['nickname']}]({node['sender']['user_id']}){node['content']}]" for node in res_json['messages']]
        msg = "合并转发内容\n" + '\n'.join(items)
    else:
        msg = str(event.message)

    record(group, id, name, uid, msg)
