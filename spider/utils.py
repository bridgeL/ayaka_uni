''' 工具包 '''

from kiana.parse import from_url
from kiana.file import create_file
from kiana.time import get_time_s_hyphen

def div_url(url:str):
    '''输入网址，自动分离简单api与参数对'''
    i = url.find('?')
    if(i == -1):
        return url, {}
    else:
        params = {}
        items = url[i+1:].split('&')
        for item in items:
            if item:
                key, val = item.split("=")
                params[key] = from_url(val)
        return url[:i], params

def combine_url(url:str, params:dict):
    items = [f"{k}={params[k]}" for k in params]
    if not items:
        return url
    return url + '?' + '&'.join(items)

def strQ2B(ustring):
    '''全角转半角 一些网页可能会用上'''
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 12288:  # 全角空格直接转换
            inside_code = 32
        elif (inside_code >= 65281 and inside_code <= 65374):  # 全角字符（除空格）根据关系转化
            inside_code -= 65248

        rstring += chr(inside_code)
    return rstring

def create_file_by_time(dirpath:str):
    if not dirpath:
        return ''

    time_s = get_time_s_hyphen()
    return create_file(f"{time_s}.log", dirpath)


