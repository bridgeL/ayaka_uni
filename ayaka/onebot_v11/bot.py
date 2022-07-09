import json
from math import ceil
from typing import Any, List, Union
from functools import partial
from typing_extensions import Protocol

from ayaka.logger import get_logger, Fore
from ayaka.utils.parse import escape, unescape
from ayaka.utils.result import ResultStore

from .event import Event
from .driver import Driver
from .message import Message, MessageSegment
from .model import DataclassEncoder


class _ApiCall(Protocol):
    async def __call__(self, **kwargs: Any) -> Any:
        ...


class Bot:
    """
    OneBot v11 协议 Bot 适配。
    """

    def __init__(self, driver: Driver):
        self.driver = driver

    def __getattr__(self, name: str) -> _ApiCall:
        return partial(self.call_api, name)

    async def call_api(self, api: str, **data) -> Any:
        """
        :说明:

          调用 OneBot 协议 API
        """
        get_logger().debug("Calling API " + Fore.YELLOW + api, module_name=__name__)

        websocket = self.driver.websocket
        if not websocket:
            get_logger().warning("没有建立ws连接，无法发送消息")
            return

        # 解决cqhttp莫名其妙被风控的问题
        data = self.safe_cqhttp_utf8(api, data)

        # 生成 seq码 和 待发送的json数据
        seq = ResultStore.get_seq()
        json_data = json.dumps(
            {"action": api, "params": data, "echo": {"seq": seq}},
            cls=DataclassEncoder,
        )

        try:
            await websocket.send(json_data)
            # 默认30s超时
            result = await ResultStore.fetch(seq, 30)
            if isinstance(result, dict):
                if result.get("status") == "failed":
                    raise
                return result.get("data")

        except:
            get_logger().error("发送消息失败，具体原因请检查cqhttp输出")

    def safe_cqhttp_utf8(self, api, data):
        if api in ["send_msg","send_group_msg","send_private_msg"]:
            data["message"] = self.cqhttp_fuck(data["message"], [119, 121, 123, 125])

        if api == "send_group_forward_msg":
            # 对每个node都要fuck一遍
            nodes = data['messages']
            for node in nodes:
                node['data']['content'] = self.cqhttp_fuck(node['data']['content'], [58,60])
            data['messages'] = nodes

        return data

    def cqhttp_fuck(self, msg, ban_range:list):
        """ 傻逼风控bug
            我怀疑是cqhttp的排版问题导致发送失败）
            该长度其实也不单是根据encode utf8长度来判断，还要根据html转义前的utf8长度判断。。傻逼
            比如&#91;占5个长度，其实相当于1个长度
        """
        # 获取utf8长度
        s = str(msg)
        s = unescape(s)
        s = s.encode('utf8')
        length = len(s)

        get_logger().debug("转义前utf8字符长度", f"{Fore.YELLOW}{length}", module_name=__name__)

        if length in ban_range:
            return str(msg) + " "
        return msg

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

        params["message"] = msg

        return await self.call_api("send_msg", **params)

    async def send_group_forward_msg(
      self,
      group_id:int,
      messages:List[str],
    ) -> None:
        # 自动分割长消息组（不可超过100条）
        n = 80
        for i in range(ceil(len(messages) / n)):
            # 自动转换为cqhttp node格式
            nodes = self.pack_message_nodes(messages[i*n: (i+1)*n])
            await self.call_api("send_group_forward_msg", group_id=group_id, messages=nodes)

    def pack_message_nodes(self, items:list):
        '''
            将数组打包为message_node格式的数组
        '''
        nodes = []
        for m in items:
            nodes.append({
                "type": "node",
                "data": {
                    "name": "Ayaka Bot",
                    "uin": "2317709898",
                    "content": str(m)
                }
            })
        return nodes

