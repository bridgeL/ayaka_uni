import re
from random import randint
from typing import Union

from kiana.file import load_json, save_json_list
from kiana.uuid import uuid6, init_ids

class Corpus:
    def __init__(self, path):
        # 从本地读取语料库
        self.path = path

        # 初始化ids库
        data = load_json(self.path)
        if data:
            ids = [str(item['id']) for item in data]
            init_ids(ids)

    def get_item(self, id):
        data = load_json(self.path)
        if not data:
            return None

        for item in data:
            if item['id'] == id:
                return item

    def del_item(self, id):
        data: list = load_json(self.path)
        if not data:
            return

        for item in data:
            if item['id'] == id:
                data.remove(item)
                break

        save_json_list(self.path, data)

    def set_item(self, id, q: Union[str, None] = None, a: Union[str, None] = None):
        data = load_json(self.path)
        if not data:
            return

        for item in data:
            if item['id'] == id:
                if q is not None:
                    item['key'] = q
                if a is not None:
                    item['value'] = a
                break

        save_json_list(self.path, data)

    def get_items(self, msg):
        data = load_json(self.path)
        if not data:
            return []

        items = []
        # 查找词汇库
        for item in data:
            key = item["key"]
            if key[0] == '=':
                # 正则匹配
                pattern = re.compile(key[1:], re.M)
                r = re.search(pattern, msg)
            else:
                # 全字匹配
                r = (msg == key)
            if r:
                items.append(item)

        return items

    def search(self, msg, random=False):
        '''
        返回对应value，如果存在多个结果，则返回第一个
        如果random为True且存在多个结果，则返回随机一个
        '''
        data = load_json(self.path)
        if not data:
            return ''

        value_list = []
        # 查找词汇库
        for item in data:
            key = item["key"]
            if key[0] == '=':
                # 正则匹配
                pattern = re.compile(key[1:], re.M)
                r = re.search(pattern, msg)
            else:
                # 全字匹配
                r = (msg == key)
            if r:
                value = item["value"]
                if type(value) is list:
                    for v in value:
                        value_list.append(v)
                else:
                    value_list.append(value)

        # 没找到结果
        if not value_list:
            return ''

        # 随机回答
        if random:
            return value_list[randint(0, len(value_list)-1)]
        return value_list[0]

    def teach(self, key, value):
        '''加入语料库，并保存到本地'''
        if key == None or value == None:
            return

        data = load_json(self.path)
        if not data:
            data = []
        data.append({"key": key, "value": value, "id": str(uuid6())})
        save_json_list(self.path, data)

    def get(self, msg):
        '''返回全部相关条目'''
        data = load_json(self.path)
        if not data:
            return []

        item_list = []
        # 查找词汇库
        for item in data:
            key = item["key"]
            if key[0] == '=':
                # 正则匹配
                pattern = re.compile(key[1:], re.M)
                r = re.search(pattern, msg)
            else:
                # 全字匹配
                r = (msg == key)

            if(r):
                item_list.append(item)

        return item_list
