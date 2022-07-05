from kiana.file import create_file, load_json, save_json_dict
from kiana.time import get_time_s

class Poetry:
    def __init__(self) -> None:
        self.path = create_file('poetry.json', 'data', '{}')

    def print_list(self):
        data = load_json(self.path)
        names = [f"《{k}》\n收录时间：{data[k]['time_s']}" for k in data]
        return '\n--------\n'.join(names)

    def get_poetry(self, name):
        data = load_json(self.path)
        for k in data:
            if k == name:
                return data[k]
        return None

    def set_last_line_num(self, name, num):
        data = load_json(self.path)
        data[name]['last_line_num'] = num
        save_json_dict(self.path, data)

    def set_poetry(self, name, lines: list):
        lines = [line for line in lines if line]
        data = load_json(self.path)
        data[name] = {
            'time_s': get_time_s(),
            'content': lines
        }
        save_json_dict(self.path, data)

