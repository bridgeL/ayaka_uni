"""本模块主要定义了 ayakabot 启动所需函数，供 bot 入口文件调用。
"""
from ayaka.logger import get_logger
from ayaka.listen import setup_ws

from ayaka.onebot_v11.driver import Driver
from ayaka.onebot_v11.adapter import Adapter

from ayaka.plugin.module import get_all_module_names, import_all_modules

_driver: Driver

def init(logger_rank=None) -> None:
    if logger_rank:
        get_logger().rank = logger_rank

    get_logger().success("Ayaka is initializing...", module_name=__name__)

    # 载入fastapi驱动器
    driver = Driver()

    global _driver
    _driver = driver

    # 载入onebot v11适配器
    adapter = Adapter(driver)

    # 载入插件
    module_names = get_all_module_names()
    import_all_modules(module_names)

    # 设置ws监听循环
    setup_ws(adapter)

    return driver.server_app


def run(*args, **kwargs) -> None:
    get_logger().success("Running Ayaka...", module_name=__name__)
    _driver.run(*args, **kwargs)
