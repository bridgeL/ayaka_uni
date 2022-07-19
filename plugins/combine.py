# from random import choice, seed, randint
# from time import time
# import re
# from typing import List
# from ayaka.lazy import *
# from pathlib import Path

# seed(time())

# path = Path.cwd().joinpath("data","combine.log")
# if not path.parent.exists():
#     path.parent.mkdir(parents=True)

# lines = path.open("r+", encoding="utf8").readlines()

# app = AyakaApp(name='combine')
# app.help = {
#     "idle":"胡言乱语 生成器\n[#combine] 开始游玩",
#     "run":"[<文字>] 回答问题\n[#exit] 退出"
# }

# cache = Cache()


# pat1 = re.compile(r"\[\d+:[\w,，]+?\]")
# pat2 = re.compile(r"\[\d+?\]")

# def load_line(line:str):
#     data = {}

#     spaces:List[str] = pat1.findall(line)
#     for space in spaces:
#         num, prompt = space[1:-1].split(":",1)
#         data[num] = prompt
#         line = line.replace(space, f"[{num}]")

#     keys = [*data.keys()]
#     n = len(keys)

#     # 随机洗牌
#     for i in range(n):
#         j = randint(i, n-1)
#         keys[i], keys[j] = keys[j], keys[i]

#     return [[key,data[key]] for key in keys], line

# @app.command(['combine', '胡言乱语'])
# async def handle(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
#     success, info = device.start_app(app.name)
#     await bot.send(event, info)

#     if success:
#         app.set_state(device,"run")
#         line = choice(lines).strip("\n")
#         data, line = load_line(line)
#         cache.set_cache(device.id, "line", data=line)
#         cache.set_cache(device.id, "data", data=data)
#         cache.set_cache(device.id, "cnt", data=0)
#         prompt = data[0][1]
#         await bot.send(event, f"[0] 请给出一个词 {prompt}")


# @app.message("run")
# async def handle(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
#     ans = event.get_plaintext().strip()

#     data = cache.get_cache(device.id, "data")
#     cnt = cache.get_cache(device.id, "cnt")

#     prompt = data[cnt][1]
#     data[cnt][1] = ans

#     await bot.send(event, f"{prompt} —— {ans}")

#     cnt += 1
#     if cnt >= len(data):
#         data_d = {}
#         for d in data:
#             data_d[d[0]] = d[1]
#         print(data_d)

#         line:str = cache.get_cache(device.id, "line")
#         spaces:List[str] = pat2.findall(line)
#         for space in spaces:
#             num = space[1:-1]
#             ans = data_d[num]
#             line = line.replace(space, ans)

#         lines = line.split("\\n")

#         await bot.send_group_forward_msg(event.group_id, lines)

#         success, info = device.stop_app()
#         if success:
#             app.set_state(device,"idle")
#         await bot.send(event, info)

#     else:
#         prompt = data[cnt][1]
#         await bot.send(event, f"[{cnt}] 请给出一个词 {prompt}")
#         cache.set_cache(device.id, "data", data=data)
#         cache.set_cache(device.id, "cnt", data=cnt)

#     return True

# @app.command(["exit","退出"], "run")
# async def handle(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
#     success, info = device.stop_app()
#     if success:
#         app.set_state(device,"idle")
#     await bot.send(event, info)



