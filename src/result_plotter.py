import matplotlib
matplotlib.use('Agg')  # 使用非交互式後端
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
import os

class ResultPlotter:
    @staticmethod
    def plot_distribution(results, strategy, img_dir='img'):
        # 嘗試使用微軟正黑體，若失敗則使用預設字型
        font_path = "C:/Windows/Fonts/msjh.ttc"
        try:
            if os.path.exists(font_path):
                font_manager.fontManager.addfont(font_path)
                prop = font_manager.FontProperties(fname=font_path)
                plt.rcParams['font.family'] = prop.get_name()
            else:
                print("警告：未找到微軟正黑體，使用預設字型")
                plt.rcParams['font.family'] = 'sans-serif'
        except Exception as e:
            print(f"字型載入失敗: {e}，使用預設字型")
            plt.rcParams['font.family'] = 'sans-serif'
        
        bins = np.arange(12, 23) - 0.5
        plt.figure(figsize=(8, 6))
        plt.hist(results, bins=bins, edgecolor='black', density=True)
        plt.title(f"{strategy} 最終手牌點數分佈")
        plt.xlabel("最終點數")
        plt.ylabel("概率")
        plt.xticks(range(12, 23))
        plt.grid(True, alpha=0.3)
        os.makedirs(img_dir, exist_ok=True)  # 確保 img_dir 存在
        plt.savefig(os.path.join(img_dir, f"{strategy}_distribution.png"))
        plt.close()

    @staticmethod
    def plot_comparison(results_dict, img_dir='img'):
        # 字型設定同上
        font_path = "C:/Windows/Fonts/msjh.ttc"
        try:
            if os.path.exists(font_path):
                font_manager.fontManager.addfont(font_path)
                prop = font_manager.FontProperties(fname=font_path)
                plt.rcParams['font.family'] = prop.get_name()
            else:
                print("警告：未找到微軟正黑體，使用預設字型")
                plt.rcParams['font.family'] = 'sans-serif'
        except Exception as e:
            print(f"字型載入失敗: {e}，使用預設字型")
            plt.rcParams['font.family'] = 'sans-serif'
        
        plt.figure(figsize=(8, 6))
        for strategy, results in results_dict.items():
            bust_rate = sum(1 for x in results if x > 21) / len(results)
            plt.bar(strategy, bust_rate, label=strategy, alpha=0.7)
        plt.title("各策略爆牌率比較")
        plt.xlabel("策略")
        plt.ylabel("爆牌率")
        plt.legend()
        plt.grid(True, alpha=0.3)
        os.makedirs(img_dir, exist_ok=True)  # 確保 img_dir 存在
        plt.savefig(os.path.join(img_dir, "strategy_comparison.png"))
        plt.close()