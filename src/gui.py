import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from blackjack_simulation import BlackjackSimulator
from result_plotter import ResultPlotter
from PIL import Image, ImageTk
import threading
import time
import json
import os
import matplotlib.pyplot as plt

class BlackjackGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("21點莊家策略模擬器")
        self.simulator = BlackjackSimulator()
        self.is_running = False
        self.show_log = tk.BooleanVar(value=False)
        self.chart_type = tk.StringVar(value="最終手牌點數分佈")
        self.strategies_cn = {
            'basic': '基本策略',
            'conservative': '保守策略',
            'aggressive': '激進策略',
            'adaptive': '自適應策略',
            'advanced': '高級自適應策略'
        }
        self.last_update_time = 0
        self.image_cache = None
        self.settings = {
            'theme': 'flatly',
            'font_size': 12,
            'update_interval': 100
        }
        self.settings_path = os.path.join('config', 'settings.json')  # 修改：設定檔案路徑
        self.img_dir = 'img'  # 修改：圖表儲存目錄
        os.makedirs(self.img_dir, exist_ok=True)  # 修改：確保 img 目錄存在
        self.expectation_window = None
        self.expectation_table = None
        self.style = None
        self.load_settings()
        self.setup_gui()
        self.root.bind('<Configure>', self.resize_images)

    def load_settings(self):
        try:
            if os.path.exists(self.settings_path):  # 修改：使用 self.settings_path
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    font_size = loaded_settings.get('font_size', 12)
                    if isinstance(font_size, int) and 8 <= font_size <= 20:
                        loaded_settings['font_size'] = font_size
                    else:
                        loaded_settings['font_size'] = 12
                    self.settings.update(loaded_settings)
        except Exception as e:
            print(f"載入設定失敗: {e}")

    def save_settings(self):
        try:
            with open(self.settings_path, 'w', encoding='utf-8') as f:  # 修改：使用 self.settings_path
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("錯誤", f"儲存設定失敗: {e}")

    def reset_settings(self):
        self.settings = {
            'theme': 'flatly',
            'font_size': 12,
            'update_interval': 100
        }
        self.apply_settings()
        self.save_settings()

    def apply_settings(self):
        try:
            if self.style is None:
                self.style = ttkb.Style(theme=self.settings['theme'])
                self.style.configure('custom.Vertical.TScrollbar', width=15)
            else:
                self.style.theme_use(self.settings['theme'])
        except Exception as e:
            messagebox.showerror("錯誤", f"主題應用失敗: {e}. 恢復預設主題 'flatly'")
            self.settings['theme'] = 'flatly'
            if self.style is None:
                self.style = ttkb.Style(theme='flatly')
                self.style.configure('custom.Vertical.TScrollbar', width=15)
            else:
                self.style.theme_use('flatly')
        
        font_size = self.settings['font_size']
        title_font_size = font_size + 12
        label_font_size = font_size
        log_font_size = max(8, font_size - 2)
        
        self.style.configure('Treeview', font=("微軟正黑體", log_font_size))
        self.style.configure('Treeview.Heading', font=("微軟正黑體", log_font_size, "bold"))
        
        for widget in self.main_frame.winfo_children():
            self.update_widget_fonts(widget, title_font_size, label_font_size, log_font_size)
        
        self.update_interval.delete(0, tk.END)
        self.update_interval.insert(0, str(self.settings['update_interval']))

    def update_widget_fonts(self, widget, title_size, label_size, log_size):
        if isinstance(widget, ttkb.Label):
            if widget.cget('text') == "21點莊家策略模擬器":
                widget.configure(font=("微軟正黑體", title_size, "bold"))
            else:
                widget.configure(font=("微軟正黑體", label_size))
        elif isinstance(widget, tk.Text):
            widget.configure(font=("微軟正黑體", log_size))
        for child in widget.winfo_children():
            self.update_widget_fonts(child, title_size, label_size, log_size)

    def open_settings(self):
        settings_window = ttkb.Toplevel(self.root)
        settings_window.title("設定")
        settings_window.geometry("400x300")
        settings_window.transient(self.root)
        settings_window.grab_set()

        frame = ttkb.Frame(settings_window, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttkb.Label(frame, text="主題：", font=("微軟正黑體", 12)).pack(anchor=tk.W, pady=5)
        theme_var = tk.StringVar(value=self.settings['theme'])
        theme_menu = ttkb.OptionMenu(
            frame,
            theme_var,
            self.settings['theme'],
            'flatly', 'darkly', 'litera'
        )
        theme_menu.pack(anchor=tk.W, pady=5)

        ttkb.Label(frame, text="文字字號（8-20）：", font=("微軟正黑體", 12)).pack(anchor=tk.W, pady=5)
        font_size_var = tk.StringVar(value=str(self.settings['font_size']))
        font_size_entry = ttkb.Entry(frame, textvariable=font_size_var, width=10)
        font_size_entry.pack(anchor=tk.W, pady=5)

        ttkb.Label(frame, text="圖表更新間隔（局）：", font=("微軟正黑體", 12)).pack(anchor=tk.W, pady=5)
        update_interval_var = tk.StringVar(value=str(self.settings['update_interval']))
        update_interval_entry = ttkb.Entry(frame, textvariable=update_interval_var, width=10)
        update_interval_entry.pack(anchor=tk.W, pady=5)

        button_frame = ttkb.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttkb.Button(
            button_frame,
            text="應用",
            command=lambda: self.apply_settings_from_window(theme_var, font_size_var, update_interval_var, settings_window),
            bootstyle=SUCCESS
        ).pack(side=tk.LEFT, padx=5)
        
        ttkb.Button(
            button_frame,
            text="儲存",
            command=lambda: [self.apply_settings_from_window(theme_var, font_size_var, update_interval_var, settings_window), 
                           self.save_settings()],
            bootstyle=PRIMARY
        ).pack(side=tk.LEFT, padx=5)
        
        ttkb.Button(
            button_frame,
            text="恢復預設值",
            command=lambda: [self.reset_settings(), theme_var.set(self.settings['theme']), 
                           font_size_var.set(str(self.settings['font_size'])), 
                           update_interval_var.set(str(self.settings['update_interval']))],
            bootstyle=SECONDARY
        ).pack(side=tk.LEFT, padx=5)

    def apply_settings_from_window(self, theme_var, font_size_var, update_interval_var, settings_window):
        try:
            font_size = int(font_size_var.get())
            if not (8 <= font_size <= 20):
                raise ValueError("文字字號必須介於 8 到 20")
            update_interval = int(update_interval_var.get())
            if update_interval <= 0:
                raise ValueError("更新間隔必須為正整數")
            self.settings.update({
                'theme': theme_var.get(),
                'font_size': font_size,
                'update_interval': update_interval
            })
            settings_window.destroy()
            self.root.after(100, self.apply_settings)
        except ValueError as e:
            messagebox.showerror("錯誤", f"無效輸入: {e}")

    def create_expectation_window(self):
        if self.expectation_window is not None:
            self.expectation_window.destroy()
        
        self.expectation_window = ttkb.Toplevel(self.root)
        self.expectation_window.title("剩餘牌期望值")
        self.expectation_window.geometry("600x180")
        self.expectation_window.transient(self.root)
        
        expectation_frame = ttkb.LabelFrame(self.expectation_window, text="剩餘牌期望值", padding=5)
        expectation_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.expectation_table = ttk.Treeview(
            expectation_frame,
            columns=['牌值', 'A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'],
            show='headings',
            height=3
        )
        self.expectation_table.heading('牌值', text='牌值')
        self.expectation_table.column('牌值', width=60, anchor='center')
        for col in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']:
            self.expectation_table.heading(col, text=col)
            self.expectation_table.column(col, width=40, anchor='center')
        self.expectation_table.pack(fill=tk.X, expand=True)

    def setup_gui(self):
        self.style = ttkb.Style(theme=self.settings['theme'])
        self.style.configure('custom.Vertical.TScrollbar', width=15)
        self.root.minsize(800, 600)
        
        self.main_frame = ttkb.Frame(self.root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        top_frame = ttkb.Frame(self.main_frame)
        top_frame.pack(fill=tk.X, pady=10)
        
        ttkb.Label(
            top_frame, 
            text="21點莊家策略模擬器", 
            font=("微軟正黑體", 24, "bold"),
            bootstyle=PRIMARY
        ).pack(pady=10)

        control_frame = ttkb.LabelFrame(self.main_frame, text="控制面板", padding=10)
        control_frame.pack(fill=tk.X, pady=10)
        
        strategy_frame = ttkb.Frame(control_frame)
        strategy_frame.pack(fill=tk.X, pady=5)
        ttkb.Label(
            strategy_frame, 
            text="選擇策略：", 
            font=("微軟正黑體", 12)
        ).pack(side=tk.LEFT)
        
        self.strategy_vars = {}
        strategies = {
            'basic': '基本策略 (17點停牌)',
            'conservative': '保守策略 (16點停牌)',
            'aggressive': '激進策略 (18點停牌)',
            'adaptive': '自適應策略 (基於爆牌概率)',
            'advanced': '高級自適應策略 (基於期望值)'
        }
        
        for strat, label in strategies.items():
            var = tk.BooleanVar(value=True)
            self.strategy_vars[strat] = var
            chk = ttkb.Checkbutton(
                strategy_frame, 
                text=label, 
                variable=var, 
                bootstyle="round-toggle"
            )
            chk.pack(side=tk.LEFT, padx=5)

        param_frame = ttkb.Frame(control_frame)
        param_frame.pack(fill=tk.X, pady=5)
        
        ttkb.Label(
            param_frame, 
            text="模擬局數：", 
            font=("微軟正黑體", 12)
        ).pack(side=tk.LEFT)
        self.num_hands = ttkb.Entry(param_frame, width=10)
        self.num_hands.insert(0, "1000")
        self.num_hands.pack(side=tk.LEFT, padx=5)
        
        ttkb.Label(
            param_frame, 
            text="模擬人數：", 
            font=("微軟正黑體", 12)
        ).pack(side=tk.LEFT)
        self.num_players = ttkb.Entry(param_frame, width=10)
        self.num_players.insert(0, "1")
        self.num_players.pack(side=tk.LEFT, padx=5)
        
        ttkb.Label(
            param_frame, 
            text="更新間隔（局）：", 
            font=("微軟正黑體", 12)
        ).pack(side=tk.LEFT)
        self.update_interval = ttkb.Entry(param_frame, width=10)
        self.update_interval.insert(0, str(self.settings['update_interval']))
        self.update_interval.pack(side=tk.LEFT, padx=5)
        
        ttkb.Checkbutton(
            param_frame,
            text="顯示牌局過程 Log",
            variable=self.show_log,
            bootstyle="round-toggle"
        ).pack(side=tk.LEFT, padx=10)

        chart_frame = ttkb.Frame(control_frame)
        chart_frame.pack(fill=tk.X, pady=5)
        ttkb.Label(
            chart_frame, 
            text="圖表類型：", 
            font=("微軟正黑體", 12)
        ).pack(side=tk.LEFT)
        self.chart_combobox = ttkb.Combobox(
            chart_frame,
            textvariable=self.chart_type,
            values=["最終手牌點數分佈", "爆牌率比較"],
            state="readonly",
            width=20
        )
        self.chart_combobox.pack(side=tk.LEFT, padx=5)

        settings_button = ttkb.Button(
            control_frame,
            text="設定",
            command=self.open_settings,
            bootstyle=INFO,
            width=15
        )
        settings_button.pack(anchor=tk.E, pady=5)

        button_frame = ttkb.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = ttkb.Button(
            button_frame, 
            text="開始模擬", 
            command=self.start_simulation, 
            bootstyle=SUCCESS,
            width=15
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttkb.Button(
            button_frame, 
            text="停止模擬", 
            command=self.stop_simulation, 
            bootstyle=DANGER,
            width=15,
            state='disabled'
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_log_button = ttkb.Button(
            button_frame, 
            text="清除 Log", 
            command=self.clear_log, 
            bootstyle=SECONDARY,
            width=15
        )
        self.clear_log_button.pack(side=tk.LEFT, padx=5)
        
        self.progress = ttkb.Progressbar(
            control_frame, 
            mode='indeterminate', 
            bootstyle=INFO
        )
        self.progress.pack(fill=tk.X, pady=10)

        self.paned_window = ttkb.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, pady=10)
        
        left_frame = ttkb.Frame(self.paned_window)
        self.paned_window.add(left_frame, weight=1)
        
        self.result_label = ttkb.Label(
            left_frame, 
            text="等待模擬開始...", 
            font=("微軟正黑體", 12)
        )
        self.result_label.pack(pady=10)
        
        self.stats_frame = ttkb.LabelFrame(left_frame, text="即時數值", padding=5)
        self.stats_frame.pack(fill=tk.X, pady=5)
        
        self.remaining_cards_label = ttkb.Label(
            self.stats_frame, 
            text="剩餘牌數：0 張", 
            font=("微軟正黑體", 12)
        )
        self.remaining_cards_label.pack(anchor=tk.W)
        
        self.shuffle_countdown_label = ttkb.Label(
            self.stats_frame, 
            text="洗牌倒計時：0 張", 
            font=("微軟正黑體", 12)
        )
        self.shuffle_countdown_label.pack(anchor=tk.W)
        
        self.avg_points_label = ttkb.Label(
            self.stats_frame, 
            text="平均點數：0.0", 
            font=("微軟正黑體", 12)
        )
        self.avg_points_label.pack(anchor=tk.W)
        
        self.bust_rate_label = ttkb.Label(
            self.stats_frame, 
            text="爆牌率：0.0%", 
            font=("微軟正黑體", 12)
        )
        self.bust_rate_label.pack(anchor=tk.W)
        
        self.total_ev_label = ttkb.Label(
            self.stats_frame, 
            text="期望點數總和：0.0", 
            font=("微軟正黑體", 12)
        )
        self.total_ev_label.pack(anchor=tk.W)
        
        log_frame = ttkb.LabelFrame(left_frame, text="牌局過程 Log", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = tk.Text(
            log_frame, 
            height=20, 
            width=50, 
            font=("微軟正黑體", 10),
            wrap=tk.WORD,
            borderwidth=2,
            relief="groove"
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttkb.Scrollbar(
            log_frame, 
            orient=tk.VERTICAL, 
            command=self.log_text.yview,
            takefocus=True,
            style='custom.Vertical.TScrollbar'
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        self.log_text.config(state='disabled')
        
        self.image_frame = ttkb.Frame(self.paned_window)
        self.paned_window.add(self.image_frame, weight=1)

        self.image_label = ttkb.Label(self.image_frame)
        self.image_label.pack(fill=tk.BOTH, expand=True)

        self.apply_settings()

    def resize_images(self, event=None):
        if not hasattr(self, 'current_image_path') or not self.current_image_path:
            return
        
        try:
            window_width = self.image_frame.winfo_width()
            window_height = self.image_frame.winfo_height()
            max_width = min(800, int(window_width * 0.8))
            max_height = min(600, int(window_height * 0.8))
            
            img = Image.open(self.current_image_path)
            img_width, img_height = img.size
            scale = min(max_width / img_width, max_height / img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            if new_width < 400:
                new_width = 400
                new_height = int(400 * img_height / img_width)
            if new_height < 300:
                new_height = 300
                new_width = int(300 * img_width / img_height)
            
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo)
            self.image_cache = photo
        except Exception as e:
            print(f"圖像加載失敗: {e}")

    def clear_log(self):
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        if self.expectation_table is not None:
            for item in self.expectation_table.get_children():
                self.expectation_table.delete(item)
        self.remaining_cards_label.config(text="剩餘牌數：0 張")
        self.shuffle_countdown_label.config(text="洗牌倒計時：0 張")
        self.avg_points_label.config(text="平均點數：0.0")
        self.bust_rate_label.config(text="爆牌率：0.0%")
        self.total_ev_label.config(text="期望點數總和：0.0")

    def update_results(self, strategy, results, logs=None, remaining_cards=None):
        if not self.is_running:
            return
        
        current_time = time.time()
        update_interval = self.settings['update_interval'] / 1000
        if current_time - self.last_update_time < update_interval:
            return
        
        self.last_update_time = current_time
        
        bust_rate = sum(1 for x in results if x > 21) / len(results) if results else 0
        self.result_label.config(
            text=f"{self.strategies_cn[strategy]}：爆牌率：{bust_rate:.2%}，模擬局數：{len(results)}"
        )
        
        total_cards = sum(remaining_cards.values()) if remaining_cards else 0
        shuffle_countdown = max(0, 124 - total_cards) if remaining_cards else 0
        avg_points = sum(min(r, 21) for r in results) / len(results) if results else 0
        self.remaining_cards_label.config(text=f"剩餘牌數：{total_cards} 張")
        self.shuffle_countdown_label.config(text=f"洗牌倒計時：{shuffle_countdown} 張")
        self.avg_points_label.config(text=f"平均點數：{avg_points:.1f}")
        self.bust_rate_label.config(text=f"爆牌率：{bust_rate:.2%}")
        
        def update_chart():
            try:
                if self.chart_type.get() == "最終手牌點數分佈":
                    ResultPlotter.plot_distribution(results, strategy, self.img_dir)  # 修改：傳遞 img_dir
                    self.current_image_path = os.path.join(self.img_dir, f"{strategy}_distribution.png")  # 修改：使用 os.path.join
                else:
                    aggregated_results = {s: [r for pid in self.simulator.results[s] for r in self.simulator.results[s][pid]] 
                                        for s in self.simulator.results}
                    ResultPlotter.plot_comparison(aggregated_results, self.img_dir)  # 修改：傳遞 img_dir
                    self.current_image_path = os.path.join(self.img_dir, "strategy_comparison.png")  # 修改：使用 os.path.join
                self.resize_images()
            except Exception as e:
                print(f"圖表更新失敗: {e}")
        
        self.root.after(0, update_chart)
        
        if self.show_log.get() and logs:
            self.log_text.config(state='normal')
            self.log_text.delete(1.0, tk.END)
            max_rounds = max(len(logs[pid]) for pid in logs)
            for round_num in range(1, max_rounds + 1):
                self.log_text.insert(tk.END, f"\n第 {round_num} 局：\n{'-'*50}\n")
                for player_id in sorted(logs.keys()):
                    if round_num <= len(logs[player_id]):
                        log = logs[player_id][round_num - 1]
                        self.log_text.insert(tk.END, f"莊家 - 玩家 {player_id}：\n{log}\n\n")
            self.log_text.config(state='disabled')
            self.log_text.see(tk.END)

        if remaining_cards and self.expectation_table:
            try:
                for item in self.expectation_table.get_children():
                    self.expectation_table.delete(item)
                total_cards = sum(remaining_cards.values())
                counts = {}
                probabilities = {}
                expected_values = {}
                point_values = {'A': 11, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10}
                total_ev = 0
                for rank in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']:
                    count = remaining_cards.get(rank, 0)
                    counts[rank] = str(count)
                    prob = count / total_cards if total_cards > 0 else 0
                    probabilities[rank] = f"{prob:.2f}"
                    ev = point_values[rank] * prob
                    expected_values[rank] = f"{ev:.2f}"
                    total_ev += ev
                self.expectation_table.insert('', 'end', values=['張數'] + [counts[rank] for rank in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']])
                self.expectation_table.insert('', 'end', values=['概率'] + [probabilities[rank] for rank in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']])
                self.expectation_table.insert('', 'end', values=['期望值'] + [expected_values[rank] for rank in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']])
                self.total_ev_label.config(text=f"期望點數總和：{total_ev:.1f}")
            except Exception as e:
                print(f"期望值表格更新失敗: {e}")

        self.root.update_idletasks()

    def start_simulation(self):
        self.is_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.clear_log_button.config(state='disabled')
        self.progress.start()
        
        num_hands = int(self.num_hands.get())
        num_players = max(1, min(10, int(self.num_players.get())))
        selected_strategies = [s for s, var in self.strategy_vars.items() if var.get()]
        
        self.create_expectation_window()
        
        def run_simulations():
            if not selected_strategies:
                self.root.after(0, lambda: self.result_label.config(text="錯誤：請至少選擇一個策略"))
                self.root.after(0, lambda: self.start_button.config(state='normal'))
                self.root.after(0, lambda: self.stop_button.config(state='disabled'))
                self.root.after(0, lambda: self.clear_log_button.config(state='normal'))
                self.root.after(0, lambda: self.progress.stop())
                self.is_running = False
                return
            
            for strategy in selected_strategies:
                if self.is_running:
                    self.simulator.run_simulation(strategy, num_hands, num_players, self.update_results)
            
            if self.is_running:
                aggregated_results = {}
                for strategy in self.simulator.results:
                    aggregated_results[strategy] = [
                        r for pid in self.simulator.results[strategy]
                        for r in self.simulator.results[strategy][pid]
                    ]
                
                if not aggregated_results:
                    self.root.after(0, lambda: self.result_label.config(text="無模擬結果"))
                else:
                    def update_final_chart():
                        try:
                            if self.chart_type.get() == "最終手牌點數分佈":
                                for strategy in aggregated_results:
                                    ResultPlotter.plot_distribution(aggregated_results[strategy], strategy, self.img_dir)  # 修改：傳遞 img_dir
                                if aggregated_results:
                                    self.current_image_path = os.path.join(self.img_dir, f"{list(aggregated_results.keys())[0]}_distribution.png")  # 修改：使用 os.path.join
                                else:
                                    self.current_image_path = None
                            else:
                                ResultPlotter.plot_comparison(aggregated_results, self.img_dir)  # 修改：傳遞 img_dir
                                self.current_image_path = os.path.join(self.img_dir, "strategy_comparison.png")  # 修改：使用 os.path.join
                            
                            if self.current_image_path:
                                self.resize_images()
                        except Exception as e:
                            print(f"最終圖表更新失敗: {e}")
                
                    self.root.after(0, update_final_chart)
                
                if self.show_log.get():
                    self.log_text.config(state='normal')
                    self.log_text.delete(1.0, tk.END)
                    for strategy in selected_strategies:
                        max_rounds = max(len(self.simulator.hand_logs[strategy][pid]) 
                                       for pid in self.simulator.hand_logs[strategy])
                        for round_num in range(1, max_rounds + 1):
                            self.log_text.insert(tk.END, f"\n第 {round_num} 局：\n{'-'*50}\n")
                            for player_id in sorted(self.simulator.hand_logs[strategy].keys()):
                                if round_num <= len(self.simulator.hand_logs[strategy][player_id]):
                                    log = self.simulator.hand_logs[strategy][player_id][round_num - 1]
                                    self.log_text.insert(tk.END, f"莊家 - 玩家 {player_id}：\n{log}\n\n")
                    self.log_text.config(state='disabled')
                    self.log_text.see(tk.END)
            
            self.root.after(0, lambda: self.start_button.config(state='normal'))
            self.root.after(0, lambda: self.stop_button.config(state='disabled'))
            self.root.after(0, lambda: self.clear_log_button.config(state='normal'))
            self.root.after(0, lambda: self.progress.stop())
            self.is_running = False
            
        threading.Thread(target=run_simulations, daemon=True).start()

    def stop_simulation(self):
        self.is_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.clear_log_button.config(state='normal')
        self.progress.stop()
        self.result_label.config(text="模擬已停止")