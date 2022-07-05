import re
from .file import create_file
from .time import get_time_s


class Logger:
    '''
字颜色:30-----------37
30:黑
31:红
32:绿
33:黄
34:蓝色
35:紫色
36:深绿
37:白色

字背景颜色范围:40----47
40:黑
41:深红
42:绿
43:黄色
44:蓝色
45:紫色
46:深绿
47:白色

字体加亮颜色:90------------97
90:黑
91:红
92:绿
93:黄
94:蓝色
95:紫色
96:深绿
97:白色

背景加亮颜色范围:100--------------------107
40:黑
41:深红
42:绿
43:黄色
44:蓝色
45:紫色
46:深绿
47:白色

作者：技术创造未来
链接：https://www.jianshu.com/p/76b1752ddcbd
来源：简书
著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。
    '''
    WHITE = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'

    def __init__(self, path='', step_mode=True) -> None:
        self.logs = []
        self.path = ''
        if path:
            self.path = create_file(path)
        self.step_mode = step_mode

    def get_clean_log(self, log):
        # 清理\033[...m
        log = re.sub(r'\033\[((\d+;)*\d+)m', '', log)
        return log

    def save_log(self, log):
        if not self.path:
            return

        f = open(self.path, 'a', encoding='utf8')

        log = self.get_clean_log(log)
        f.write(log + '\n')

        f.close()

    def save_logs(self):
        if not self.path:
            return

        f = open(self.path, 'a', encoding='utf8')

        for log in self.logs:
            log = self.get_clean_log(log)
            f.write(log + '\n')

        f.close()

        self.logs = []

    def print_log(self, log):
        print(log)
        self.save_log(log)

    def print_logs(self):
        for log in self.logs:
            print(log)
        self.save_logs()

    def base_log(self, color, *texts: str):
        # 强制str
        texts = [str(t) for t in texts]

        # 获取时间
        time_s = get_time_s()
        time_s = f"{color}{time_s}{self.WHITE}"

        log = ' '.join([time_s, *texts])

        if self.step_mode:
            self.print_log(log)
        else:
            self.logs.append(log)

    def success(self, *texts: str):
        text = f"[{self.GREEN}SUCCESS{self.WHITE}]"
        self.base_log(self.GREEN, text, *texts)

    def warning(self, *texts: str):
        text = f"[{self.YELLOW}WARNING{self.WHITE}]"
        self.base_log(self.YELLOW, text, *texts)

    def error(self, *texts: str):
        text = f"[{self.RED}ERROR{self.WHITE}]"
        self.base_log(self.RED, text, *texts)

    def info(self, *texts: str):
        self.base_log(self.GREEN, '[INFO]', *texts)

    def debug(self, *texts: str):
        text = f"[{self.CYAN}DEBUG{self.WHITE}]"
        self.base_log(self.CYAN, text, *texts)

    def blank(self):
        self.print_log('')
