import time
from typing import Union


# 获得时间 或 转换时间
def get_time_i(time_s: str = '', format: str = r'%Y/%m/%d %H:%M:%S'):
    '''
        - time_s存在时，转换time_s为对应time_i，time_s必须完整包含时间、日期
        - time_s缺失时，则返回当前时间日期
    '''
    if not time_s:
        return int(time.time())
    t = time.strptime(time_s, format)
    return int(time.mktime(t))


def get_time_s(time_i: Union[int, None] = None, format: str = r'%Y/%m/%d %H:%M:%S'):
    '''
        - time_i存在时，转换time_i为对应time_s，time_i必须是正确的时间戳
        - time_i缺失时，则返回当前时间日期
    '''
    t = time.localtime(time_i)
    return time.strftime(format, t)


# 其他衍生
def get_time_s_hyphen(time_i: Union[int, None] = None):
    '''
        - time_i存在时，转换time_i为对应time_s，time_i必须是正确的时间戳
        - time_i缺失时，则返回当前时间日期（连字符格式）
    '''
    return get_time_s(time_i, r'%Y-%m-%d %H-%M-%S')


# 获取纯时间
def get_time_i_pure(time_s: str = '', format: str = r"%H:%M:%S"):
    '''
        - time_s存在时，转换time_s为对应time_i，time_s仅包含时间
        - time_s缺失时，则返回当前时间（仅时间）

        time_i的范围是 -28800 ~ 57600
    '''
    if time_s:
        time_s = '1970/01/02 ' + time_s
    time_i = get_time_i(time_s, r"%Y/%m/%d " + format)
    return (time_i + 28800) % 86400 - 28800


def get_time_s_pure(time_i: Union[int, None] = None, format: str = r"%H:%M:%S"):
    '''
        - time_i存在时，转换time_i为对应time_s，time_i的范围是 -28800 ~ 57600
        - time_i缺失时，则返回当前时间（仅时间）
    '''
    if time_i is not None:
        time_i += 86400
    return get_time_s(time_i, format)


# 其他衍生
def get_time_s_pure_hyphen(time_i: Union[int, None] = None):
    '''
        - time_i存在时，转换time_i为对应time_s，time_i的范围是 -28800 ~ 57600
        - time_i缺失时，则返回当前时间（仅时间）（连字符格式）
    '''
    return get_time_s_pure(time_i, r'%H-%M-%S')


# 获得日期 或 转换日期
def get_date_i(date_s: str = '', format: str = r'%Y/%m/%d'):
    '''
        - date_s存在时，转换date_s为对应date_i
        - date_s缺失时，则返回当前日期

        返回的日期以1970/01/01 为 0 起始点， 输入的日期若早于该起始点，则会报错
    '''
    if date_s:
        time_s = date_s + ' 8:00:00'
        time_i = get_time_i(time_s, format + r" %H:%M:%S")
    else:
        time_i = get_time_i()
    return int((time_i + 28800) / 86400)


def get_date_s(date_i: Union[int, None] = None, format: str = r'%Y/%m/%d'):
    '''
        - date_i存在时，转换date_i为对应date_s
        - date_i缺失时，则返回当前日期

        输入的date_i必须非负，0 对应 1970/01/01
    '''
    if date_i is None:
        return get_time_s(None, format)
    time_i = date_i * 86400
    return get_time_s(time_i, format)


# 其他衍生
def get_date_s_hyphen(date_i: Union[int, None] = None):
    return get_date_s(date_i, r'%Y-%m-%d')
