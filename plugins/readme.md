## 一定要修改pyproject.toml

```ini
[tool.nonebot]
plugins = ["src.main"]
plugin_dirs = []
```

## 所有插件编写的基本编写格式

- 新建app（插件对象）
```python
app = AyakaApp(
    name = "unknown",
)
# area ALL、GROUP、PRIVATE，指定插件可以对哪些会话生效
# name 插件名字
```
- 编写指令，并给出状态要求（默认为idle）
```python
# 所有插件的初始状态都是idle
@app.command([命令1,命令2,...],[状态1,状态2,...],trigger_share)
async def handle(bot, event, device):
    # 必须是async函数
    # bot 为 Onebot V11 的 Bot对象
    # event 为 Onebot V11 的 MessageEvent对象
    # device 为 AyakaDevice对象

    # 设置指定device下，app的state
    app.set_state(device, "menu")
    pass
```
