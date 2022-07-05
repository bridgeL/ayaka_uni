import re
def check_integer(arg):
    t = type(arg)
    if t is str:
        return not re.search(r'[^0-9\-]',arg)
    if t is list or t is tuple:
        return False
    return arg == int(arg)

def safe_get_list_item(items:list, i:int):
    if i < 0 or i >= len(items):
        return False, None
    return True, items[i]

