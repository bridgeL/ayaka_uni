from typing import Any, List, Union
from functools import partial
from typing_extensions import Protocol
from ayaka.div import pack_message_nodes

from ayaka.utils import escape

from .message import Message, MessageSegment
from .event import Event
from .adapter import Adapter


class _ApiCall(Protocol):
    async def __call__(self, **kwargs: Any) -> Any:
        ...


class Bot:
    """
    OneBot v11 协议 Bot 适配。
    """

    def __init__(self, adapter: Adapter, self_id: str):
        self.adapter = adapter
        """协议适配器实例"""
        self.self_id = self_id
        """机器人 ID"""

    def __getattr__(self, name: str) -> _ApiCall:
        return partial(self.call_api, name)

    @property
    def name(self) -> str:
        """协议适配器名称"""
        return self.adapter.get_name().upper()

    async def call_api(self, api: str, **data) -> Any:
        """
        :说明:

          调用 OneBot 协议 API
        """
        try:
            result = await self.adapter._call_api(self.self_id, api, **data)
        except:
            raise

        return result

    async def send(
        self,
        event: Event,
        message: Union[str, Message, MessageSegment],
        **kwargs,
    ) -> Any:
        """
        :说明:

          根据 ``event``  向触发事件的主体发送消息。
        """

        # 转义处理
        if isinstance(message, str):
            message = escape(message, escape_comma=False)

        # 生成Message
        if isinstance(message, Message):
            msg = message
        else:
            msg = Message(message)

        params = {}

        # 填写目标id
        if getattr(event, "user_id", None):
            params["user_id"] = getattr(event, "user_id")
        if getattr(event, "group_id", None):
            params["group_id"] = getattr(event, "group_id")
        params.update(kwargs)

        # 填写群聊/私聊
        if "message_type" not in params:
            if params.get("group_id", None):
                params["message_type"] = "group"
            elif params.get("user_id", None):
                params["message_type"] = "private"
            else:
                raise ValueError("Cannot guess message type to reply!")

        # # 发送回复时，at回复人
        # if params["message_type"] != "private":
        #     params["message"] = MessageSegment.at(params["user_id"]) + " " + msg

        params["message"] = msg

        return await self.call_api("send_msg", **params)

    async def send_group_forward_msg(
      self,
      group_id:int,
      messages:List[str],
    ) -> None:
        nodes = pack_message_nodes(messages)
        return await self.call_api("send_group_forward_msg", group_id=group_id, messages=nodes)
