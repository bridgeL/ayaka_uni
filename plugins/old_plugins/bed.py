from kiana.time import get_time_i_pure, get_time_s_pure
from ayaka.lazy import *
from ayaka.utils import pack_message_nodes

__help__ = {
    "name": "bed",
    "idle": "快滚去睡觉",
}

title = '''警钟敲烂

[2022年6月14日] 孙剑 博士 人工智能 45岁'''

lines = [
'''[2022年6月14日] 孙剑 博士 人工智能 45岁
孙剑平时爱运动，喜欢骑车。孙剑在13日晚还进行了夜跑，而14日凌晨猝死！''',

'''[2011年2月] 《柳叶刀》 导致猝死的十大影响因素：
交通尾气污染（PAF值为7.4%）
用力过度（6.2%)
饮酒(5.0%)
喝咖啡(5.0%)
空气污染(PM10＞30μg/m3)(4.8%)
抑郁情绪(3.9%)
发怒(3.1%)
暴饮暴食(2.7%)
情绪过于激动(2.4%)
过度性生活(2.2%)
吸食可卡因(0.9%)
吸食大麻(0.8%)
呼吸道感染(0.6%)
——《Public health importance of triggers of myocardial infarction: a comparative risk assessment》（心肌梗死的诱发因素对公共健康影响的重要性——可对比的风险评估）

注：PAF是一个评估暴露的人群作用的非常常见的流行病学指标，表达的意思是如果某个暴露取消，结局会减少的百分比''',

    ]

nodes = pack_message_nodes(lines)

app = AyakaApp(name='bed',area=AyakaAppArea.GROUP,help=__help__)

@app.everyday('23:00:00')
async def handle(bot:Bot):
    await bot.send_group_msg(group_id=666214666, message=f"{get_time_s_pure()} 敏娜桑，该睡觉了")
    await bot.send_group_msg(group_id=666214666, message=title)
    await bot.call_api('send_group_forward_msg', group_id=666214666, messages=nodes)

@app.everyday('12:00:00')
async def handle(bot:Bot):
    time_i = get_time_i_pure()
    time_i += 11*3600
    time_i = (time_i+28800) % 86400 - 28800
    await bot.send_group_msg(group_id=666214666, message=f"{get_time_s_pure(time_i)} wty快去睡觉")
    await bot.send_group_msg(group_id=666214666, message=title)
    await bot.call_api('send_group_forward_msg', group_id=666214666, messages=nodes)

@app.command(['bed','滚去睡觉','睡觉','该睡觉了','快去睡觉'])
async def test(bot:Bot, event:GroupGroupMessageEvent, device:AyakaDevice):
    await bot.send_group_msg(group_id=666214666, message=f"{get_time_s_pure()} 该睡觉了")
    await bot.send(event, title)
    await bot.call_api('send_group_forward_msg', group_id=event.group_id, messages=nodes)


