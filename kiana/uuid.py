from random import sample, seed
from string import digits, ascii_lowercase, ascii_uppercase
from time import time

# 初始化随机数种子
seed(time())
# 随机数库
chars_bin = digits + ascii_lowercase + ascii_uppercase

ids = set()

def init_ids(_ids:list):
    global ids
    ids = set(_ids)

def _create_id(num=6):
    """仅可模块内部使用"""
    return ''.join(sample(chars_bin, num))

def create_id(num=6) -> str:
    '''生成6位id，不保证不重复'''
    id = _create_id(num)

    ids.add(id)
    return id

def create_id_no_repeat(num=6) -> str:
    """生成唯一id"""
    id = _create_id(num)
    while id in ids:
        # 对于100k数量级的数据，6位碰撞的概率已经足够低
        id = _create_id(num)

    ids.add(id)
    return id

def uuid6() -> str:
    return create_id_no_repeat(6)
