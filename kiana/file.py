from io import FileIO
import json
import os


def create_file(path: str, dirpath: str = '', default: str = ''):
    # 生成完整路径
    if dirpath:
        dirpath = dirpath.rstrip('/')
        path = f"{dirpath}/{path}"

    # 分离路径和文件名
    items = path.rsplit('/', 1)
    if len(items) == 1:
        items.insert(0, '.')
    dirpath, filename = items

    # 自动创建路径
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    # 自动创建文件
    if filename not in os.listdir(dirpath):
        f = open(path, 'w+', encoding='utf8')
        f.write(default)
        f.close()

    return path


def load_json(path: str):
    '''从指定路径加载json数据，如果为空或文件已损坏返回None'''
    f = open(path, 'r', encoding='utf8')
    s = f.read()
    f.close()
    try:
        return json.loads(s)
    except:
        return None


def save_json(path: str, data: dict):
    '''向指定路径保存json数据'''
    json.dump(data, open(path, 'w+', encoding='utf8'), ensure_ascii=False)


def save_json_list(path: str, data: list):
    '''向指定路径保存列表，一行一条'''
    f = open(path, 'w+', encoding='utf8')
    tab = "    "
    f.write('[\n')

    for i, d in enumerate(data):
        s = json.dumps(d, ensure_ascii=False)
        f.write(f"{tab}{s}")
        if i < len(data) - 1:
            f.write(",")
        f.write("\n")

    f.write(f"]\n")

def _check_big(data):
    '''
    需要分行
    data = {
        a : {}
    }

    不需要分行
    data = { a : sdf }
    data = sdf
    '''
    if isinstance(data, dict):
        for v in data.values():
            if isinstance(v, dict):
                return True
    return False

def _save_dict(f:FileIO, data: dict, level: int):
    '''特别定制'''

    if _check_big(data):
        tab = "    "
        t = tab * level

        f.write("{")

        keys = list(data.keys())
        for i, key in enumerate(keys):
            val = data[key]
            f.write("\n" + t + tab + f'"{key}": ')
            _save_dict(f, val, level+1)

            if i < len(keys) - 1:
                f.write(',')

        f.write("\n" + t + "}")
    else:
        s = json.dumps(data, ensure_ascii=False)
        f.write(s)

def save_json_dict(path: str, data: dict):
    """特别定制"""
    f = open(path, 'w+', encoding='utf8')
    _save_dict(f, data, 0)


