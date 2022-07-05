import json
import asyncio
from typing import Any, Dict, List

from ayaka.utils import DataclassEncoder, ResultStore, _handle_api_result, unescape
from ayaka.logger import Fore, get_logger

from .model import WebSocketServerSetup
from .driver import Driver, FastAPIWebSocket
from .message import Message


class Adapter:
    def __init__(self, driver: Driver):
        self.driver = driver
        self.connections: Dict[str, FastAPIWebSocket] = {}
        self.tasks: List["asyncio.Task"] = []

    @classmethod
    def get_name(cls) -> str:
        return "Ayaka Bot"

    def setup_websocket_server(self, setup: WebSocketServerSetup):
        """设置一个 WebSocket 服务器路由配置"""
        if not isinstance(self.driver, Driver):
            raise TypeError("Current driver does not support websocket server")
        self.driver.setup_websocket_server(setup)

    def cqhttp_fuck(self, data):
        """ 傻逼风控bug
            我怀疑是cqhttp的排版问题导致发送失败）
            该长度其实也不单是根据encode utf8长度来判断，还要根据html转义前的utf8长度判断。。傻逼
            比如&#91;占5个长度，其实相当于1个长度
        """
        s = str(data["message"])
        s = unescape(s)
        bs = s.encode('utf8')
        get_logger().debug("转义前utf8字符长度", f"{Fore.YELLOW}{len(bs)}", module_name=__name__)

        if len(bs) in [119, 121, 123, 125]:
            s += ' '
            data["message"] = Message(s)
        return data


    async def _call_api(self, bot_id: str, api: str, **data: Any) -> Any:
        if api in ["send_msg","send_group_msg","send_private_msg"]:
            data = self.cqhttp_fuck(data)

        websocket = self.connections.get(bot_id, None)
        get_logger().debug("Calling API " + Fore.YELLOW + api, module_name=__name__)
        if websocket:
            seq = ResultStore.get_seq()
            json_data = json.dumps(
                {"action": api, "params": data, "echo": {"seq": seq}},
                cls=DataclassEncoder,
            )
            await websocket.send(json_data)

            # 默认30s超时
            return _handle_api_result(
                await ResultStore.fetch(bot_id, seq, 30)
            )

        else:
            raise


