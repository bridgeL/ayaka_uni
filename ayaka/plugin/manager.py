import asyncio
from html import unescape

from ayaka.logger import get_logger
from kiana.time import get_date_s, get_time_i_pure

from ayaka.onebot_v11.event import Event, MessageEvent, GroupMessageEvent, Reply
from ayaka.onebot_v11.bot import Bot

from .app import AyakaAppManager
from .device import AyakaDevice


class EventManager:
    def __init__(self, apps: AyakaAppManager, bot: Bot) -> None:
        self.apps = apps
        self.bot = bot

    def log(self, event: Event):
        log_msg = event.get_log_string()
        if log_msg:
            log_msg = unescape(log_msg)
            get_logger().success(log_msg)

    async def deal(self, event: Event):
        """处理一个事件。调用该函数以实现分发事件 """

        # 展示消息
        self.log(event)

        # 目前只处理群聊消息
        if isinstance(event, GroupMessageEvent):
            # 将 回复 移动到event对应的属性上
            await self.deal_reply(event)
            try:
                await self.deal_group_message_event(event)
            except:
                get_logger().exception()

    async def deal_group_message_event(self, event: GroupMessageEvent):
        '''处理消息事件'''
        # 生成device
        device = AyakaDevice(id=event.group_id)

        # 运行监视触发
        supervise_list = self.apps.get_supervise_list()
        tasks = [asyncio.create_task(func(self.bot, event, device))
                 for func in supervise_list]

        await asyncio.gather(*tasks)

        # 获得所有可用的触发
        triggers = self.apps.get_triggers(device)

        # 根据命令长度从高到低排序
        # command trigger将自然排列在message trigger前
        triggers.sort(key=lambda x: x.command, reverse=True)

        text = str(event.message)
        for trigger in triggers:

            if trigger.command:
                # 遍历command trigger
                if text.startswith(f"#{trigger.command}"):
                    await trigger.handler(self.bot, event, device)
                    return

            else:
                # 遍历message trigger
                if await trigger.handler(self.bot, event, device):
                    return

        get_logger().success(f"没有任何匹配项")

    async def deal_reply(self, event: MessageEvent):
        """
        检查消息中存在的回复，去除并赋值 ``event.reply``
        """

        items = [(i, ms) for i, ms in enumerate(event.message) if ms.type == "reply"]
        if not items:
            return
        index, msg_seg = items[0]

        try:
            data = await self.bot.get_msg(message_id=msg_seg.data["id"])
            event.reply = Reply.parse_obj(data)
        except Exception as e:
            get_logger().warning(f"Error when getting message reply info: {repr(e)}", e, module_name=__name__)
        else:
            del event.message[index]

    async def deal_heartbeat(self):
        # 还要改
        date_s = get_date_s()
        time_i = get_time_i_pure()
        for timer in AyakaAppManager.timers:
            if timer.date_s != date_s:
                # 一分钟之内响应，过时不候
                if timer.time_i < time_i and timer.time_i + 60 > time_i:
                    # if timer.time_i < time_i:
                    timer.date_s = date_s
                    await timer.func(self.bot)
