from re import A
from typing import List
from ayaka.div import div_cmd_arg
from ayaka.lazy import *
from random import randint
from plugins.bag import add_money, get_name

app = AyakaApp(name='cat')
app.help = "小猫钓鱼，花费1000金为鱼钩挂上一张扑克，共52张\n如果匹配则拿走对应的牌，获得等价的奖励\nJ牌拿走全部，但J牌本身不奖励\nQ牌双倍奖励\nK牌四倍奖励\n玩家每购买一张扑克，bot也会购买一张\n被拿走的牌会立刻洗入牌堆\n[#cat <数字>] 购买扑克n次 [#catt <数字>] bot购买扑克n次"

cache = Cache()


class CatGame:
    unit = 1000

    def __init__(self, device_id) -> None:
        # st
        self.ST = Storage(device_id, 'cat', 'table')

        # 生成一套牌
        self.heap: List[str] = []
        for i in ['♣', '♠', '♦️', '♥️']:
            # 2 - 10
            self.heap.extend([f'{i}{j+2}' for j in range(9)])
            # A JQK
            self.heap.extend([f'{i}{j}' for j in ['A', 'J', 'Q', 'K']])

        # 读取历史牌桌
        self.table: List[str] = self.ST.get([])

        # 移除已在桌面上的牌
        for card in self.table:
            self.heap.remove(card)

    @classmethod
    def get_card_code(cls, card: str):
        '''
        这里必须灵活移除，长度不一致（囧，否则会有隐藏（不打印）的unicode符号残留，导致后续判断出错
        * ♣ len 1
        * ♠ len 1
        * ♦️ len 2
        * ♥️ len 2
        '''
        return card.lstrip('♣♠♦️♥️')

    @classmethod
    def get_card_value(cls, card: str):
        code = cls.get_card_code(card)
        if code == 'J':
            return 0
        if code == 'Q':
            return cls.unit * 2
        if code == 'K':
            return cls.unit * 4
        return cls.unit

    @classmethod
    def get_cards_value(cls, cards: list):
        ms = [cls.get_card_value(card) for card in cards]
        return sum(ms)

    def match(self, card: str):
        '''判断是否得分，并且返回可拿走的牌组的编号'''
        code = self.get_card_code(card)
        if code == 'J':
            return 0

        codes = [self.get_card_code(card) for card in self.table]
        print('codes', codes)
        if code in codes:
            return codes.index(code)
        return -1

    def add_card(self, card: str):
        '''根据获得的牌进行相关处理'''

        # 是否赢牌
        i = self.match(card)
        if i >= 0:
            gain, self.table = self.table[i:], self.table[:i]
            gain.append(card)
            # 这些牌重新洗入牌堆(不用洗，因为取牌时就是随机的)
            self.heap.extend(gain)
        else:
            gain = []
            self.table.append(card)

        # 保存修改后的桌面
        self.ST.set(self.table)
        return gain

    def pull(self):
        '''抽一张卡'''
        i = randint(0, len(self.heap)-1)
        card = self.heap.pop(i)

        return self.add_card(card), card

    def get_info(self):
        # 展示当前桌面
        if self.table:
            value = self.get_cards_value(self.table)
            return '目前桌面\n' + '\n'.join(self.table) + f'\n桌面总价值 {value}金'
        else:
            return '目前桌面为空'


def game_pull(device_id: int, cnt=1):
    game: CatGame = cache.get_cache(device_id)
    if not game:
        game = CatGame(device_id)

    # 抽卡
    all_gain = []
    gains = []
    cards = []

    for i in range(cnt):
        gain, card = game.pull()
        gains.append(gain)
        cards.append(card)
        all_gain.extend(gain)

    # 桌面信息
    info = game.get_info()

    cache.set_cache(device_id, data=game)
    return all_gain, gains, cards, info


def get_cnt(event:GroupMessageEvent):
    cmd, args, arg = div_cmd_arg('cat',event.message)
    try:
        cnt = int(args[0])
        if cnt < 1:
            cnt = 1
        if cnt > 10:
            cnt = 10
    except:
        cnt = 1
    return cnt


@app.command('cat')
async def bag(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    cnt = get_cnt(event)

    # 付费
    add_money(-CatGame.unit*cnt, event=event)

    # 抽卡
    gain, gains, cards, info = game_pull(device.id, cnt)
    card = "\n".join(cards)

    # 生成提示信息
    items = []
    name = get_name(event)
    items.append(f"[{name}] 花费 {CatGame.unit*cnt}金购买了{cnt}张卡\n{card}")

    # 结算
    money = CatGame.get_cards_value(gain)
    add_money(money, event=event)
    if len(gain) == 0:
        items.append(f"[{name}] 颗粒无收")
    else:
        ss = ["\n".join(g) for g in gains if g]
        s = "\n------\n".join(ss)
        items.append(f"[{name}] 拿走了\n{s}\n总计 {money}金")

    items.append(info)
    await bot.send_group_forward_msg(event.group_id, items)


@app.command('catt')
async def bag(bot: Bot, event: GroupMessageEvent, device: AyakaDevice):
    cnt = get_cnt(event)

    # 抽卡
    gain, gains, cards, info = game_pull(device.id, cnt)
    card = "\n".join(cards)

    # 生成提示信息
    items = []
    name = "bot"
    items.append(f"[{name}] 添加了{cnt}张卡\n{card}")

    # 结算
    money = CatGame.get_cards_value(gain)
    if len(gain) > 0:
        ss = ["\n".join(g) for g in gains if g]
        s = "\n------\n".join(ss)
        items.append(f"[{name}] 拿走了\n{s}\n总计 {money}金")

    items.append(info)
    await bot.send_group_forward_msg(event.group_id, items)
