from pydantic import BaseModel

from .storage import Storage

class AyakaDevice(BaseModel):
    """现阶段只接受群聊"""
    id: int
    group: bool = True

    def get_app_name(self):
        return Storage(self.id, 'app').get()

    def set_app_name(self, name):
        return Storage(self.id, 'app').set(name)

    def start_app(self, app_name):
        _app_name = self.get_app_name()

        if _app_name:
            if _app_name != _app_name:
                info = f"[{_app_name}] 正在运行，请先关闭 [{_app_name}] 后再次尝试启动 [{app_name}]"
            else:
                info = f"[{app_name}] 已经启动，无需重复启动"
            return False, info

        self.set_app_name(app_name)
        return True, f"[{app_name}] 成功启动"

    def stop_app(self):
        app_name = self.get_app_name()
        self.set_app_name('')
        return True, f"已关闭应用 [{app_name}]"


