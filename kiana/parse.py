from html import escape, unescape
from urllib.parse import quote, unquote
def to_url(text:str):
    '''URI转义

    - 举例：%20
    '''
    return quote(text, safe=':/?&=')

def from_url(text:str):
    return unquote(text)

def to_html(text:str):
    '''HTML转义

    - 举例：\&amp;
    '''
    return escape(text)

def from_html(text:str):
    return unescape(text)

def api_params_to_url(api:str, params:dict):
    items = [f"{k}={params[k]}" for k in params]
    url = api + '?' + '&'.join(items)
    return url

def url_to_api_params(url:str):
    if '?' not in url:
        return url, {}

    api, left = url.split('?',maxsplit=1)

    params = {}
    items = left.split('&')
    for item in items:
        k,v = item.split('=',maxsplit=1)
        params[k] = v

    return api, params
