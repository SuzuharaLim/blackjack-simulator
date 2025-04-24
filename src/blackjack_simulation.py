from deck import Deck
from collections import defaultdict
import numpy as np

class BlackjackSimulator:
    def __init__(self, num_decks=6):
        self.num_decks = num_decks
        self.total_cards = num_decks * 52  # 6 副牌共 312 張
        self.shuffle_threshold = int(self.total_cards * 0.4)  # 40% 即 124 張
        self.results = defaultdict(lambda: defaultdict(list))  # 結構: {strategy: {player_id: [results]}}
        self.expected_values = defaultdict(dict)  # 結構: {strategy: {player_id: ev}}
        self.hand_logs = defaultdict(lambda: defaultdict(list))  # 結構: {strategy: {player_id: [logs]}}
        
    def get_card_value(self, card):
        """計算單張牌的點數，移除花色"""
        rank = card[:-1] if card[-1] in ['♠', '♥', '♦', '♣'] else card
        if rank in ['J', 'Q', 'K']:
            return 10
        if rank == 'A':
            return 11
        return int(rank)
    
    def calculate_total(self, hand):
        """計算手牌總點數"""
        total = 0
        aces = 0
        for card in hand:
            if card[:-1] == 'A':  # 檢查牌值是否為 A（忽略花色）
                aces += 1
            total += self.get_card_value(card)
        
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total
    
    def basic_strategy(self, hand):
        """基本策略：小於 17 點補牌，17 點以上停牌"""
        return self.calculate_total(hand) < 17
    
    def conservative_strategy(self, hand):
        """保守策略：16點停牌"""
        return self.calculate_total(hand) < 16
    
    def aggressive_strategy(self, hand):
        """激進策略：18點停牌"""
        return self.calculate_total(hand) < 18
    
    def adaptive_strategy(self, hand, deck):
        """自適應策略：基於爆牌概率"""
        total = self.calculate_total(hand)
        if total < 12:
            return True
        
        if 12 <= total <= 16:
            remaining = deck.get_remaining_cards()
            total_cards = sum(remaining.values())
            if total_cards == 0:
                return False
                
            bust_cards = 0
            for card, count in remaining.items():
                if self.get_card_value(card) + total > 21:
                    bust_cards += count
            bust_prob = bust_cards / total_cards
            return bust_prob < 0.4
        return False
    
    def advanced_adaptive_strategy(self, hand, deck):
        """高級自適應策略：基於期望值"""
        total = self.calculate_total(hand)
        if total < 12:
            return True
            
        if 12 <= total <= 18:
            remaining = deck.get_remaining_cards()
            total_cards = sum(remaining.values())
            if total_cards == 0:
                return False
                
            stand_value = min(total, 21)
            hit_value = 0
            for card, count in remaining.items():
                temp_hand = hand + [card]
                temp_total = self.calculate_total(temp_hand)
                hit_value += (count / total_cards) * min(temp_total, 21)
            
            return hit_value > stand_value
        return False
    
    def simulate_hand(self, strategy, strategy_name, player_id, deck, round_num):
        """模擬莊家一手牌，並記錄過程"""
        # 檢查剩餘牌數，低於 40% 時洗牌
        remaining_cards = len(deck.cards)
        if remaining_cards <= self.shuffle_threshold:
            deck.shuffle()
            log = [f"牌堆剩餘 {remaining_cards} 張，低於 40%（{self.shuffle_threshold} 張），已將用過的牌放回並洗牌"]
        else:
            log = []
        
        # 起始兩張牌
        hand = [deck.draw(), deck.draw()]
        log.append(f"初始手牌: {hand}, 點數: {self.calculate_total(hand)}")
        
        # 補牌邏輯
        while strategy(hand, deck) if strategy_name in ['adaptive', 'advanced'] else strategy(hand):
            new_card = deck.draw()
            hand.append(new_card)
            log.append(f"補牌: {new_card}, 當前手牌: {hand}, 點數: {self.calculate_total(hand)}")
        
        final_total = self.calculate_total(hand)
        log.append(f"最終結果: 點數 {final_total}{' (爆牌)' if final_total > 21 else ''}")
        self.hand_logs[strategy_name][player_id].append("\n".join(log))
        return final_total, deck.get_remaining_cards()
    
    def calculate_expected_value(self, strategy_name, player_id, results):
        """計算策略的期望值"""
        valid_results = [min(r, 21) for r in results]
        return np.mean(valid_results)
    
    def run_simulation(self, strategy_name, num_hands, num_players, update_callback=None):
        """運行多玩家輪流模擬"""
        strategies = {
            'basic': self.basic_strategy,
            'conservative': self.conservative_strategy,
            'aggressive': self.aggressive_strategy,
            'adaptive': self.adaptive_strategy,
            'advanced': self.advanced_adaptive_strategy
        }
        
        decks = {pid: Deck(self.num_decks) for pid in range(1, num_players + 1)}
        self.results[strategy_name] = {pid: [] for pid in range(1, num_players + 1)}
        self.hand_logs[strategy_name] = {pid: [] for pid in range(1, num_players + 1)}
        
        for round_num in range(1, num_hands + 1):
            for player_id in range(1, num_players + 1):
                result, remaining_cards = self.simulate_hand(
                    strategies[strategy_name], 
                    strategy_name, 
                    player_id, 
                    decks[player_id], 
                    round_num
                )
                self.results[strategy_name][player_id].append(result)
                if update_callback:
                    all_results = [r for pid in self.results[strategy_name] 
                                 for r in self.results[strategy_name][pid]]
                    update_callback(strategy_name, all_results, self.hand_logs[strategy_name], remaining_cards)
        
        for player_id in range(1, num_players + 1):
            self.expected_values[strategy_name][player_id] = self.calculate_expected_value(
                strategy_name, player_id, self.results[strategy_name][player_id]
            )