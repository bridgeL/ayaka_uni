import sys
import traceback
from colorama import Fore, init
from datetime import datetime
import logging

def get_time_s_now():
    return datetime.now().strftime("%m-%d %H:%M:%S")

class Logger:
    rank_dict = {
        "DEBUG": 0,
        "INFO": 1,
        "SUCCESS": 2,
        "WARNING": 3,
        "ERROR": 4,
    }

    def __init__(self, rank="INFO", path="", show_module_name=True) -> None:
        # DEBUG INFO SUCCESS WARN ERROR NONE, 依次升高过滤等级, 能看到的消息也逐级减少
        self.rank = rank
        self.path = path
        self.show_module_name = show_module_name

    def level(self, rank):
        if rank not in self.rank_dict:
            return 10
        return self.rank_dict[rank]

    def print_log(self, *items, module_name=None, rank="INFO"):
        # 检查
        if not self.check(rank): return

        # 时间
        time_s = Fore.GREEN + get_time_s_now() + Fore.RESET

        # rank
        if rank == "DEBUG":
            rank = f"[{Fore.BLUE}DEBUG{Fore.RESET}]"
        elif rank == "SUCCESS":
            rank = f"[{Fore.GREEN}SUCCESS{Fore.RESET}]"
        elif rank == "WARNING":
            rank = f"[{Fore.YELLOW}WARNING{Fore.RESET}]"
        elif rank == "ERROR":
            rank = f"[{Fore.LIGHTRED_EX}ERROR{Fore.RESET}]"
        else:
            rank = f"[{rank}]"

        # 模块名
        if module_name:
            module_name = self.color_module_name(module_name)

        # 生成items
        if self.show_module_name and module_name:
            items = [time_s, rank, module_name, *items]
        else:
            items = [time_s, rank, *items]

        # 强制序列化
        items = [str(item) for item in items]

        # 输出到std
        print(" ".join(items))

        # 保存到指定文件 还没写
        if self.path:
            pass

    def check(self, rank):
        return self.level(self.rank) <= self.level(rank)

    def color_module_name(self, module_name):
        return Fore.CYAN + module_name + Fore.RESET + " |"

    def debug(self, *items, module_name=None):
        self.print_log(*items, module_name=module_name, rank="DEBUG")

    def info(self, *items, module_name=None):
        self.print_log(*items, module_name=module_name, rank="INFO")

    def success(self, *items, module_name=None):
        self.print_log(*items, module_name=module_name, rank="SUCCESS")

    def warning(self, *items, module_name=None):
        self.print_log(*items, module_name=module_name, rank="WARNING")

    def error(self, *items, module_name=None):
        self.print_log(*items, module_name=module_name, rank="ERROR")

    def exception(self):
        _, info, trace = sys.exc_info()
        traceback.print_tb(trace)
        self.error(info)

init(autoreset=True)  # 初始化，并且设置颜色设置自动恢复
_logger = Logger()

def get_logger():
    """不用logger._logger，而用logger.get_logger() 这样显得我们很正规~"""
    return _logger

class UvicornLogger(logging.Handler):  # pragma: no cover
    def emit(self, record):
        name = record.levelname
        msg = record.getMessage()

        if name == "DEBUG":
            _logger.debug(msg, module_name="uvicorn")
        elif name == "INFO":
            _logger.info(msg, module_name="uvicorn")
        elif name == "SUCCESS":
            _logger.success(msg, module_name="uvicorn")
        elif name == "WARNING":
            _logger.warning(msg, module_name="uvicorn")
        elif name == "ERROR":
            _logger.error(msg, module_name="uvicorn")
        else:
            _logger.print_log(f"[{Fore.MAGENTA}{name}{Fore.RESET}]", msg, module_name="uvicorn")



