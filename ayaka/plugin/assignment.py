from ayaka.onebot_v11.bot import Bot
from ayaka.onebot_v11.event import Event, GroupMessageEvent
from ayaka.logger import get_logger, Fore
from kiana.time import get_date_s, get_time_i_pure, get_time_s_pure

from .app import app_list, timer_list
from .device import AyakaDevice


async def assign_event(bot: Bot, event: Event):
    # 目前只处理群聊消息
    if isinstance(event, GroupMessageEvent):
        # if event.group_id == 905028333:
        #     await bot.send(event, '嗷嗷')
        await deal_message(bot, event)


async def deal_message(bot: Bot, event: GroupMessageEvent):
    '''处理消息事件'''
    # get_logger().success(f'{Fore.MAGENTA}{bot.name}{Fore.RESET} 收到群聊消息')

    '''查找device

    输入：event
    输出：device
    '''
    device = AyakaDevice(id=event.group_id)

    # app_name = device.get_app_name()
    # if app_name:
    #     get_logger().success(
    #         f"{Fore.CYAN}{device.id}{Fore.RESET}", "|",
    #         f"正在运行 {Fore.YELLOW}{app_name}{Fore.RESET}"
    #     )

    '''遍历plugin

    输入:device
    输出：trigger list
    '''
    triggers = app_list.get_triggers(device)

    '''根据命令长度从高到低排序

    command trigger将自然排列在message trigger前
    '''
    triggers.sort(key=lambda x: x.command, reverse=True)

    text = str(event.message)
    for trigger in triggers:

        if trigger.command:
            '''遍历command trigger

            输入：bot, event, device
            '''

            if text.startswith(f"#{trigger.command}"):
                get_logger().success(
                    "触发插件",
                    f"{Fore.YELLOW}{trigger.plugin_name}{Fore.RESET}", "|",
                    f"{Fore.CYAN}{trigger.state}{Fore.RESET}", "|",
                    f"{Fore.GREEN}{trigger.command}{Fore.RESET}"
                )
                await trigger.handler(bot, event, device)
                return

        else:
            '''遍历message trigger

            输入：bot, event, device
            '''
            get_logger().success(
                "触发插件",
                f"{Fore.YELLOW}{trigger.plugin_name}{Fore.RESET}"
            )

            if await trigger.handler(bot, event, device):
                return

    get_logger().success(f"没有任何匹配项")
    if event.get_plaintext().startswith('#'):
        await bot.send(event, "你可以试试#help 或 #exit")


async def deal_heartbeat(bot):
    date_s = get_date_s()
    time_i = get_time_i_pure()
    for timer in timer_list:
        if timer.date_s != date_s:
            # 一分钟之内响应，过时不候
            if timer.time_i < time_i and timer.time_i + 60 > time_i:
                # if timer.time_i < time_i:
                timer.date_s = date_s
                await timer.func(bot)
                time_s = get_time_s_pure(timer.time_i)
                get_logger().success(
                    "触发定时器",
                    f"{Fore.YELLOW}{timer.plugin_name}{Fore.RESET}",
                    f"{time_s}"
                )
