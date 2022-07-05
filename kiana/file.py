import json
import os

def create_file(path:str, dirpath:str='', default:str=''):
    # 生成完整路径
    if dirpath:
        dirpath = dirpath.rstrip('/')
        path = f"{dirpath}/{path}"

    # 分离路径和文件名
    items = path.rsplit('/',1)
    if len(items) == 1:
        items.insert(0, '.')
    dirpath, filename = items

    # 自动创建路径
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    # 自动创建文件
    if filename not in os.listdir(dirpath):
        f = open(path,'w+',encoding='utf8')
        f.write(default)
        f.close()

    return path

def load_json(path:str):
    '''从指定路径加载json数据，如果为空或文件已损坏返回None'''
    f = open(path,'r',encoding='utf8')
    s = f.read()
    f.close()
    try:
        return json.loads(s)
    except:
        return None

def save_json(path:str, data:dict):
    '''向指定路径保存json数据'''
    json.dump(data, open(path,'w+',encoding='utf8'), ensure_ascii=False)

def save_json_list(path:str, data:list):
    '''向指定路径保存列表，一行一条'''
    f = open(path,'w+',encoding='utf8')
    f.write('[\n')
    for d in data[:-1]:
        s = json.dumps(d,ensure_ascii=False)
        f.write(s + ',\n')

    s = json.dumps(data[-1],ensure_ascii=False)
    f.write(s + '\n]')

def save_json_dict(path:str, data:dict):
    '''向指定路径保存字典，一行一对kv'''
    f = open(path,'w+',encoding='utf8')
    f.write('{\n')

    def _write(k, end=',\n'):
        d = data[k]
        s = json.dumps(d,ensure_ascii=False) + end
        f.write(f"\"{k}\":{s}")

    keys = list(data.keys())
    for k in keys[:-1]:
        _write(k)

    k = keys[-1]
    _write(k,'\n}')
