# 过渡到sql
from kiana.file import create_file, load_json, save_json_dict

class Storage:
    '''持久化数据'''
    def __init__(self, id, *keys) -> None:
        self.path = create_file(f"{id}.json", 'data/storage', '{}')
        self.keys = [str(k) for k in keys]

    def inc(self):
        '''+1s'''
        data = self.get(0)
        data += 1
        self.set(data)

    def set(self, _data):
        path = self.path
        keys = self.keys

        # 读取文件
        data = load_json(path)

        # 留着后续保存
        whole_data = data

        # 赋值
        for key in keys[:-1]:
            if key not in data:
                data[key] = {}
            data = data[key]

        data[keys[-1]] = _data

        # 保存文件
        save_json_dict(path, whole_data)

    def get(self, default=None, write=False):
        '''
            当查找不到值时，返回默认值default
            当write为True时，还会自动写入default值到本地
        '''
        path = self.path
        keys = self.keys

        # 读取文件
        data = load_json(path)

        # 查找值
        for key in keys:
            if key in data:
                data = data[key]
            else:
                data = default
                if write:
                    self.set(default)
                break

        # 返回
        return data

class Cache:
    '''临时数据'''
    def __init__(self) -> None:
        self.cache = {}

    def set_cache(self, keys:list, _data):
        data = self.cache

        # 赋值
        for key in keys[:-1]:
            if key not in data:
                data[key] = {}
            data = data[key]
        data[keys[-1]] = _data

    def get_cache(self, *keys:str):
        data = self.cache

        # 查找值
        for key in keys:
            if key in data:
                data = data[key]
            else:
                return None
        return data
