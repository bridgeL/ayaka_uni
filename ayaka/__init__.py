"""本模块主要定义了 ayakabot 启动所需函数，供 bot 入口文件调用。
"""
import json
import asyncio

from ayaka.logger import get_logger

from ayaka.onebot_v11.bot import Bot
from ayaka.onebot_v11.event import json_to_event
from ayaka.onebot_v11.driver import Driver, FastAPIWebSocket

from ayaka.plugin.manager import EventManager
from ayaka.plugin.app import AyakaAppManager


_driver: Driver


def init(logger_rank=None) -> None:
    if logger_rank:
        get_logger().rank = logger_rank

    get_logger().success("Ayaka is initializing...", module_name=__name__)

    # 载入插件
    apps = AyakaAppManager()

    # 载入fastapi驱动器
    driver = Driver()

    global _driver
    _driver = driver

    # 载入ayaka bot
    bot = Bot(driver)

    # 载入manager
    manager = EventManager(apps, bot)

    # 配置ws监听
    async def _handle_ws(websocket: FastAPIWebSocket):
        await handle_ws(websocket, manager)
    driver.setup("Ayaka Bot", "/ayakabot", _handle_ws)

    return driver.server_app


def run(*args, **kwargs) -> None:
    get_logger().success("Running Ayaka...", module_name=__name__)
    _driver.run(*args, **kwargs)


async def handle_ws(websocket: FastAPIWebSocket, manager: EventManager) -> None:
    # 建立ws连接
    await websocket.accept()
    _driver.websocket = websocket

    try:
        # 监听循环
        while True:
            data = await websocket.receive()
            json_data = json.loads(data)
            # 将json解析为对应的event
            event = json_to_event(json_data)
            if event:
                asyncio.create_task(manager.deal(event))
    except:
        get_logger().exception()
    finally:
        # 结束ws连接
        await websocket.close()
        _driver.websocket = None
