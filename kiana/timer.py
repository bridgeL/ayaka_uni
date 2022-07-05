from time import time_ns
class Timer:
    '''
        统计与上次记录的时间差值
    '''
    def __init__(self) -> None:
        self.last = 0

    def click(self, name:str = ''):
        time_i = time_ns()
        diff = time_i - self.last
        self.last = time_i
        print(f"{diff/1000000} ms", name)
