import json
import asyncio
from typing import Any, Optional

from ayaka.utils import ResultStore
from ayaka.logger import Fore, get_logger

from ayaka.plugin.assignment import assign_event

from ayaka.onebot_v11.bot import Bot
from ayaka.onebot_v11.event import Event, MessageEvent, Reply, get_event_model
from ayaka.onebot_v11.adapter import Adapter
from ayaka.onebot_v11.message import MessageSegment
from ayaka.onebot_v11.model import URL, WebSocketServerSetup
from ayaka.onebot_v11.driver import FastAPIWebSocket

def setup_ws(adapter: Adapter):
    async def __handle(websocket: FastAPIWebSocket):
        await _handle_ws(adapter, websocket)

    ws_setup = WebSocketServerSetup(
        URL("/ayakabot"),
        adapter.get_name(),
        __handle
    )
    adapter.setup_websocket_server(ws_setup)


async def _handle_ws(adapter: Adapter, websocket: FastAPIWebSocket) -> None:
    bot_id = websocket.request.headers.get("x-self-id")

    await websocket.accept()

    # 新建bot
    bot = Bot(adapter, bot_id)
    adapter.connections[bot_id] = websocket

    get_logger().info(
        f"{Fore.YELLOW}Bot {bot_id}{Fore.RESET} connected", module_name=__name__)

    try:
        while True:
            data = await websocket.receive()
            json_data = json.loads(data)
            event = json_to_event(json_data, bot_id)
            if event:
                asyncio.create_task(handle_event(bot, event))
    except:
        pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
        adapter.connections.pop(bot_id, None)


def json_to_event(
    json_data: Any, bot_id: Optional[str] = None
) -> Optional[Event]:
    if not isinstance(json_data, dict):
        return None

    if "post_type" not in json_data:
        if bot_id is not None:
            ResultStore.add_result(bot_id, json_data)
        return

    try:
        post_type = json_data["post_type"]
        detail_type = json_data.get(f"{post_type}_type")
        detail_type = f".{detail_type}" if detail_type else ""
        sub_type = json_data.get("sub_type")
        sub_type = f".{sub_type}" if sub_type else ""
        models = get_event_model(post_type + detail_type + sub_type)
        for model in models:
            try:
                event = model.parse_obj(json_data)
                break
            except Exception as e:
                get_logger().debug("Event Parser Error", e, module_name=__name__)
        else:
            event = Event.parse_obj(json_data)

        return event
    except Exception as e:
        get_logger().error(
            f"{Fore.RED}Failed to parse event.\nRaw: {json_data}{Fore.RESET}",
            e, module_name=__name__)


async def _check_reply(bot: "Bot", event: MessageEvent):
    """
    :说明:

      检查消息中存在的回复，去除并赋值 ``event.reply``, ``event.to_me``

    :参数:

      * ``bot: Bot``: Bot 对象
      * ``event: Event``: Event 对象
    """
    try:
        index = list(map(lambda x: x.type == "reply",
                     event.message)).index(True)
    except ValueError:
        return
    msg_seg = event.message[index]
    try:
        data = await bot.call_api("get_msg", message_id=msg_seg.data["id"])
        event.reply = Reply.parse_obj(data)
    except Exception as e:
        get_logger().warning(
            f"Error when getting message reply info: {repr(e)}", e, module_name=__name__)
        return
    # ensure string comparation
    if str(event.reply.sender.user_id) == str(event.self_id):
        event.to_me = True
    del event.message[index]
    if len(event.message) > index and event.message[index].type == "at":
        del event.message[index]
    if len(event.message) > index and event.message[index].type == "text":
        event.message[index].data["text"] = event.message[index].data["text"].lstrip()
        if not event.message[index].data["text"]:
            del event.message[index]
    if not event.message:
        event.message.append(MessageSegment.text(""))


def _check_at_me(event: MessageEvent):
    """
    :说明:

      检查消息开头或结尾是否存在 @机器人，去除并赋值 ``event.to_me``

    :参数:

      * ``bot: Bot``: Bot 对象
      * ``event: Event``: Event 对象
    """
    if not isinstance(event, MessageEvent):
        return

    # ensure message not empty
    if not event.message:
        event.message.append(MessageSegment.text(""))

    if event.message_type == "private":
        event.to_me = True
    else:

        def _is_at_me_seg(segment: MessageSegment):
            return segment.type == "at" and str(segment.data.get("qq", "")) == str(
                event.self_id
            )

        # check the first segment
        if _is_at_me_seg(event.message[0]):
            event.to_me = True
            event.message.pop(0)
            if event.message and event.message[0].type == "text":
                event.message[0].data["text"] = event.message[0].data["text"].lstrip()
                if not event.message[0].data["text"]:
                    del event.message[0]
            if event.message and _is_at_me_seg(event.message[0]):
                event.message.pop(0)
                if event.message and event.message[0].type == "text":
                    event.message[0].data["text"] = (
                        event.message[0].data["text"].lstrip()
                    )
                    if not event.message[0].data["text"]:
                        del event.message[0]

        if not event.to_me:
            # check the last segment
            i = -1
            last_msg_seg = event.message[i]
            if (
                last_msg_seg.type == "text"
                and not last_msg_seg.data["text"].strip()
                and len(event.message) >= 2
            ):
                i -= 1
                last_msg_seg = event.message[i]

            if _is_at_me_seg(last_msg_seg):
                event.to_me = True
                del event.message[i:]

        if not event.message:
            event.message.append(MessageSegment.text(""))


async def handle_event(bot: Bot, event: Event) -> None:
    """处理一个事件。调用该函数以实现分发事件 """
    # 展示消息
    log_msg = f"{Fore.MAGENTA}{bot.type.upper()} {bot.self_id}{Fore.RESET} | "
    try:
        log_msg += event.get_log_string()
    except:
        pass
    else:
        get_logger().success(log_msg)

    if isinstance(event, MessageEvent):
        # 将 回复/at 移动到event对应的属性上
        await _check_reply(bot, event)
        _check_at_me(event)

        # 传递bot和event
        try:
            await assign_event(bot, event)
        except:
            get_logger().exception()
