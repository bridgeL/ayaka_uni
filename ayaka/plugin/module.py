# 导入src/plugins下的所有插件
import importlib
import os
import re

from ayaka.logger import get_logger, Fore

# 函数
def get_all_module_names(path='plugins'):
    '''
        获取标准模块名
    '''
    file_names = os.listdir(path)
    head = re.sub(r"\\|/", ".", path).rstrip('.') + '.'
    get_logger().debug("尝试导入", Fore.YELLOW + path + Fore.RESET, "下的所有插件", module_name=__name__)

    def get_module_name(file_name: str):
        # 文件
        if '.' in file_name:
            if file_name.endswith('.py'):
                return head + file_name[:-3]
            return None

        # 包
        # 排除python缓存文件夹
        if not file_name.startswith('__'):
            return head + file_name
        return None

    raw_module_names = [get_module_name(file_name) for file_name in file_names]

    # 排除None
    return [name for name in raw_module_names if name != None]


def import_all_modules(module_names):
    '''
        根据模块名导入模块
    '''
    for module_name in module_names:
        try:
            module = importlib.import_module(module_name)
            get_logger().debug("已导入", module, module_name=__name__)
            get_logger().success(f"{Fore.YELLOW}{module_name}{Fore.RESET} 导入成功", module_name=__name__)
        except:
            get_logger().exception()
            get_logger().error(f"{Fore.YELLOW}{module_name}{Fore.RESET} 导入失败", module_name=__name__)
