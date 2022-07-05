"""需要大改"""

from typing import List, Union
from kiana.div import div_head, split_by_space
from ayaka.onebot_v11.message import Message

def div_arg(msg:Message):
    '''根据类型和空格分割，得到参数数组'''
    args:List[str] = []
    for ms in msg:
        if ms.type == 'text':
            ts = split_by_space(str(ms))
            args.extend(ts)
        else:
            args.append(str(ms))
    return args

def div_cmd_arg(_cmds:Union[str,list], msg:Message):
    '''根据类型和空格分割，得到参数数组，并返回响应的cmd'''
    text = str(msg)
    if not text.startswith('#'):
        cmd = ''
        args = [text]
        left = text.strip()
    else:
        cmd, left = div_head(_cmds, text[1:])

        # 根据类型和空格分割，得到参数数组
        args = div_arg(msg)

        # 由于第一个参数包含命令，因此需要删除命令部分
        _ , arg = div_head(f"#{cmd}",args[0])

        # 若删除后没有剩余，则直接剔除该参数
        if not arg: args.pop(0)
        else: args[0] = arg

    return cmd, args, left


def pack_message_nodes(items:list):
    '''
        将数组打包为message_node格式的数组
    '''
    nodes = []
    for m in items:
        nodes.append({
            "type": "node",
            "data": {
                "name": "Ayaka Bot",
                "uin": "2317709898",
                "content": str(m)
            }
        })
    return nodes
