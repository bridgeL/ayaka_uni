"""这里只留存我们关心的数据"""

import re
from kiana.time import get_time_s
from pydantic import BaseModel

from ayaka.logger import get_logger

pattern = re.compile(
    r"^((https|http)://)?"                      # 协议
    r"(([0-9]{1,3}\.){3}[0-9]{1,3}"             # IP形式的URL- 199.194.52.184
    r"|"                                        # 允许IP和DOMAIN（域名）
    r"([0-9a-z_!~*'()-]+\.)*"                   # 域名- www.
    r"([0-9a-z][0-9a-z-]{0,61})?[0-9a-z]\."     # 二级域名
    r"[a-z]{2,6})"                              # first level domain- .com or .museum
    r"(:[0-9]{1,4})?"                           # 端口- :80
    r"((/?)|"                                   # a slash isn't required if there is no file name
    r"(/[0-9a-z_!~*'().;?:@&=+$,%#-]+)+/?)$",   # 参数
    re.I
)


class BaseMeta(BaseModel):
    urls: list
    tag: str = ""
    title: str = ""
    desc: str = ""
    raw_data: dict

    def __init__(self, data: dict) -> None:
        urls = []
        for k in data:
            v = str(data[k])

            # 排除图标
            k = str(k)
            if "icon" in k.lower():
                continue

            # 只解析http/https或无协议的链接
            r = pattern.search(v)
            if r:
                urls.append(r.group())

        super().__init__(urls=urls, raw_data=data, **data)


class BaseJson(BaseModel):
    app: str
    # com.tencent.miniapp_01 小程序
    # com.tencent.structmsg 小卡片
    # com.tencent.mobileqq.cardshare 好友分享
    desc: str = ""
    prompt: str
    ctime_s: str
    meta_key: str
    meta_val: BaseMeta

    def __init__(self, meta: dict, **data) -> None:
        ctime = data['config']['ctime']
        ctime_s = get_time_s(ctime)

        keys = list(meta.keys())
        if len(keys) != 1:
            get_logger().warning("meta具有令人意外的长度")

        meta_key = keys[0]
        meta_val = BaseMeta(meta[meta_key])
        super().__init__(
            meta_key=meta_key,
            meta_val=meta_val,
            ctime_s=ctime_s,
            **data
        )
