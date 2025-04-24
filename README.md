21點莊家策略模擬器
這是一個基於 Python 的模擬工具，用於分析和視覺化 21 點（Blackjack）中不同的莊家策略。專案實現了多種策略（基本策略、保守策略、激進策略、自適應策略和高級自適應策略），並提供圖形使用者介面（GUI）來運行模擬、查看即時統計數據並生成分析報告。
功能

多種策略：模擬莊家行為，包含五種策略：
基本策略（17 點停牌）
保守策略（16 點停牌）
激進策略（18 點停牌）
自適應策略（基於爆牌機率）
高級自適應策略（基於期望值）


圖形介面：使用 tkinter 和 ttkbootstrap 構建互動式控制介面，即時顯示統計數據和視覺化結果。
即時統計：模擬過程中顯示剩餘牌數、洗牌倒計時、平均點數、爆牌率和期望值。
視覺化：使用 matplotlib 生成手牌點數分佈直方圖和爆牌率比較柱狀圖。
分析報告：生成詳細的 Markdown 報告，比較各策略的爆牌率、平均點數和期望值。
可自訂設定：透過設定視窗調整主題、字型大小和更新間隔，儲存於 config/settings.json。

安裝

複製儲存庫：
git clone https://github.com/your-username/blackjack-simulator.git
cd blackjack-simulator


建立虛擬環境（建議）：
python -m venv venv
source venv/bin/activate  # Windows 上使用：venv\Scripts\activate


安裝依賴項：
pip install -r requirements.txt


確保字型支援：

專案使用微軟正黑體（msjh.ttc）來渲染圖表中的繁體中文文字。請確保系統中已安裝此字型（Windows 預設包含）。若無此字型，程式會自動回退到 sans-serif 字型，但可能影響中文顯示效果。



使用方法

啟動應用程式：
python src/main.py


圖形介面操作：

選擇策略：勾選要模擬的策略（預設全選）。
設定參數：輸入模擬局數（預設 1000 局）和玩家數量（預設 1 人，最大 10 人）。
圖表類型：選擇「最終手牌點數分佈」或「爆牌率比較」。
顯示日誌：勾選以顯示詳細牌局日誌。
設定：調整主題、字型大小和更新間隔。
開始/停止：啟動或停止模擬。
清除日誌：重置日誌和統計顯示。


輸出結果：

即時統計：顯示剩餘牌數、洗牌倒計時、平均點數、爆牌率和期望值。
圖表：儲存於 img/ 目錄（例如 img/strategy_comparison.png、img/<strategy>_distribution.png）。
分析報告：儲存為 reports/analysis_report.md，包含策略比較和分析結論。



專案結構
blackjack-simulator/
├── src/
│   ├── gui.py                 # 使用 tkinter 和 ttkbootstrap 實現圖形介面
│   ├── analysis_report.py     # 生成 Markdown 報告和期望值比較圖表
│   ├── main.py                # 應用程式入口
│   ├── blackjack_simulation.py # 核心模擬邏輯，實現各種策略
│   ├── deck.py                # 牌堆管理和抽牌邏輯
│   ├── result_plotter.py      # 圖表生成函數
├── config/
│   ├── settings.json          # 主題、字型大小和更新間隔的設定
├── img/
│   ├── .gitkeep               # 保留空目錄
│   ├── (生成的圖表)          # 儲存圖表，如 strategy_comparison.png
├── reports/
│   ├── .gitkeep               # 保留空目錄
│   ├── (生成的報告)          # 儲存報告，如 analysis_report.md
├── README.md                  # 專案說明文件
├── requirements.txt           # Python 依賴項清單
├── .gitignore                 # Git 忽略檔案

依賴項
請參閱 requirements.txt 獲取完整清單。主要依賴包括：

Python 3.8+
tkinter（通常隨 Python 附帶）
ttkbootstrap 用於圖形介面樣式
matplotlib 用於圖表繪製
numpy 用於數值計算
Pillow 用於圖片處理

注意事項

字型設定：圖表預設使用微軟正黑體（C:/Windows/Fonts/msjh.ttc）。若不可用，程式會回退到 sans-serif 字型，可能影響中文顯示。
目錄要求：請確保 img/ 和 reports/ 目錄可寫入，圖表和報告將儲存於此。
模擬規模：大量的局數或玩家數可能增加運行時間。透過設定中的更新間隔平衡響應速度和效能。
執行緒安全：模擬在獨立執行緒中運行以保持圖形介面響應，但停止模擬可能需要片刻完成。

貢獻
歡迎貢獻！請遵循以下步驟：

Fork 本儲存庫。
建立功能分支（git checkout -b feature/your-feature）。
提交變更（git commit -m "Add your feature"）。
推送至分支（git push origin feature/your-feature）。
提交 Pull Request。

授權
本專案採用 MIT 授權，詳情請見 LICENSE 文件（待新增）。
致謝

使用 tkinter、ttkbootstrap 和 matplotlib 構建。
靈感來自 21 點策略分析與模擬專案。

