from enum import Enum
from typing import Callable, List, Union
from pydantic import BaseModel

from ayaka.logger import get_logger, Fore
from kiana.time import get_time_i_pure

from .storage import Storage
from .device import AyakaDevice


class AyakaTrigger(BaseModel):
    plugin_name: str
    state: str      # 使用state和command实现触发间的隔离
    command: str    # 为空是消息触发，否则是命令触发
    handler: Callable


class Timer(BaseModel):
    time_i: int
    date_s: str = ''
    plugin_name: str
    func: Callable


class AyakaApp:
    def __init__(
        self,
        name: str = "test",
    ) -> None:
        self.name = name
        self.triggers: List[AyakaTrigger] = []
        self._help = {"idle": "测试用例"}

        app_list.add_plugin(self)

    @property
    def help(self):
        return self._help

    @help.setter
    def help(self, help):
        self._help = help
        help_dict[self.name] = help

    def get_state(self, device: AyakaDevice):
        return Storage(device.id, self.name, 'state').get(default="idle")

    def set_state(self, device: AyakaDevice, state: str):
        Storage(device.id, self.name, 'state').set(state)

    def command(
        self,
        cmds: Union[str, List[str]],
        states: Union[str, List[str]] = 'idle',
    ):
        def _decorator(func: Callable):
            _cmds = [cmds] if type(cmds) is str else cmds
            _states = [states] if type(states) is str else states

            cmd_str = ' '.join(
                [f"[{Fore.GREEN}{c}{Fore.RESET}]" for c in _cmds])

            for state in _states:
                for cmd in _cmds:
                    trigger = AyakaTrigger(
                        plugin_name=self.name,
                        state=state,
                        command=cmd,
                        handler=func
                    )
                    self.triggers.append(trigger)
                get_logger().info(
                    f"{Fore.YELLOW}{self.name}{Fore.RESET}", "|",
                    f"状态[{Fore.CYAN}{state}{Fore.RESET}]",
                    f"新增命令触发{cmd_str}"
                )
            return func

        return _decorator

    def message(
        self,
        state: str = 'idle',
    ):
        def _decorator(func: Callable):
            trigger = AyakaTrigger(
                plugin_name=self.name,
                state=state,
                command="",
                handler=func
            )
            self.triggers.append(trigger)
            get_logger().info(
                f"{Fore.YELLOW}{self.name}{Fore.RESET}", "|",
                f"状态[{Fore.CYAN}{state}{Fore.RESET}]",
                "新增消息触发"
            )
            return func

        return _decorator

    def everyday(self, time_s: str):
        def _decorator(func: Callable):
            time_i = get_time_i_pure(time_s)
            timer = Timer(time_i=time_i, func=func, plugin_name=self.name)
            timer_list.append(timer)
            get_logger().info(
                f"{Fore.YELLOW}{self.name}{Fore.RESET}", "|",
                f"新增每日定时触发 {time_s}"
            )
            return func

        return _decorator


class AyakaAppList:
    def __init__(self) -> None:
        self.items: List[AyakaApp] = []

    def add_plugin(self, plugin: AyakaApp):
        # # 避免重复添加
        # for plugin in self.items:
        #     if plugin.name == plugin.name:
        #         return
        self.items.append(plugin)

    def get_plugin(self, name: str):
        for plugin in self.items:
            if plugin.name == name:
                return plugin
        return None

    def get_triggers(self, device: AyakaDevice):
        app_name = device.get_app_name()
        if app_name:
            plugin = self.get_plugin(app_name)
            if plugin:
                # 返回其当前状态的trigger
                state = plugin.get_state(device)
                triggers = [t for t in plugin.triggers if t.state == state]
                return triggers

            # 出现问题，任何正在运行的plugin都至少应该有一个trigger
            # 否则device将一直处于无应答的状态
            get_logger().error(f"设备可能永久运行该应用，无法退出 [{app_name}]\n{device}")
            raise
        else:
            # 仅提取所有插件的idle状态下的触发器
            # 当插件不处于idle状态时，能转发消息到该插件的设备
            # 一定是正在运行该插件的设备
            triggers: List[AyakaTrigger] = []
            for plugin in self.items:
                ts = [t for t in plugin.triggers if t.state == 'idle']
                triggers.extend(ts)

            return triggers


# 插件池
app_list = AyakaAppList()

# timer池
timer_list: List[Timer] = []

# 帮助列表
help_dict = {}
