from ayaka.utils.parse import unescape
from kiana.file import create_file
from kiana.time import get_date_s_hyphen, get_time_s

def record(group:bool, id:int, name, uid, message):
    date_s = get_date_s_hyphen()

    head = "group" if group else "private"
    path = create_file(f"{date_s}.log", f"data/record/{head}/{id}")

    message = unescape(str(message))
    text = f'[{get_time_s()}] {name}({uid}) 说: {message}'
    with open(path, 'a+', encoding='utf8') as f:
        f.write(f'{text}\n')
