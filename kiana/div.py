from typing import List, Union


def div_head(_heads:Union[str, List[str]], text:str):
    '''
        如果text的开头与heads中的某个head相同（如果有多个，则选择最长的）

        返回该head，以及text的剩余部分
    '''
    heads = [_heads] if type(_heads) is str else _heads
    heads.sort(key=lambda x:len(x),reverse=True)
    for head in heads:
        if text.startswith(head):
            return head, text[len(head):].strip()
    return '', text.strip()

def split_by_space(text:str):
    '''
        将text根据空格分割为多个子串

        排除空子串
    '''
    items = text.strip().split(' ')
    items = [i for i in items if i]
    return items

def div_cmd_args(_cmds:Union[str, List[str]], text:str):
    '''
        分离命令与参数，返回触发的命令、参数列表、排除了命令的剩余部分
    '''
    cmds = [_cmds] if type(_cmds) is str else _cmds
    cmds = [f"#{cmd}" for cmd in cmds]
    cmd, left = div_head(cmds, text)
    args = split_by_space(left)
    return cmd, args, left.strip()
