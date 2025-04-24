import random

class Deck:
    def __init__(self, num_decks=1):
        """初始化牌堆，包含 num_decks 副牌（每副 52 張）"""
        self.num_decks = num_decks
        self.ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        self.suits = ['♠', '♥', '♦', '♣']
        self.cards = []
        self.used_cards = []  # 新增：追蹤已用牌
        self.reset()

    def reset(self):
        """重置牌堆，生成 num_decks 副新牌"""
        self.cards = [rank + suit for rank in self.ranks for suit in self.suits] * self.num_decks
        self.used_cards = []  # 清空已用牌
        random.shuffle(self.cards)

    def shuffle(self):
        """洗牌，將已用牌放回牌堆並隨機重排"""
        # 將已用牌放回牌堆
        self.cards.extend(self.used_cards)
        self.used_cards = []  # 清空已用牌
        random.shuffle(self.cards)

    def draw(self):
        """抽一張牌，若牌堆空則洗牌"""
        if not self.cards:
            self.shuffle()
        card = self.cards.pop()
        self.used_cards.append(card)  # 記錄已用牌
        return card

    def get_remaining_cards(self):
        """返回剩餘牌的計數字典（僅包含 self.cards）"""
        counts = {}
        for card in self.cards:
            rank = card[:-1] if card[-1] in ['♠', '♥', '♦', '♣'] else card
            counts[rank] = counts.get(rank, 0) + 1
        return counts