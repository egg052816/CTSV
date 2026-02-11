import os
import re
import json
import subprocess
import time


class RetryManager:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.log_path = os.path.join(self.base_dir, "execution_log.txt")
        self.retry_list = {}  # 格式: {'1_Clock.py': ['Error msg...'], ...}

    def analyze_log(self):
        """ 步驟 1: 分析 Log 檔找出失敗的腳本 """
        if not os.path.exists(self.log_path):
            print(f"  [Retry] 找不到 Log 檔: {self.log_path}，無法執行重試。")
            return

        print(f"  [Retry] 正在分析 Log 以建立重試清單...")

        current_script = None

        try:
            with open(self.log_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()

                # 1. 偵測目前跑到哪個腳本 (抓取 .py 檔名)
                # 邏輯：Batch 檔執行時會印出 python D:\...\1_Clock.py
                # 我們抓取以 .py 結尾的單詞
                if ".py" in line and "Python" in line:
                    # 嘗試抓取檔名
                    parts = line.split()
                    for part in parts:
                        if part.endswith(".py"):
                            filename = os.path.basename(part)
                            # 排除掉 Setup, Clean, Retry 本身
                            if filename not in ["Clean_Setup.py", "End_Clean_Env.py", "Retry.py"]:
                                current_script = filename

                # 2. 偵測失敗標記 [Fail]
                if "[Fail]" in line and current_script:
                    if current_script not in self.retry_list:
                        self.retry_list[current_script] = []

                    # 避免重複紀錄
                    fail_msg = line.split("[Fail]")[1].strip() if "[Fail]" in line else line
                    if fail_msg not in self.retry_list[current_script]:
                        self.retry_list[current_script].append(fail_msg)

        except Exception as e:
            print(f"  [Retry] 分析過程發生錯誤: {e}")

    def execute_retry(self):
        """ 步驟 2: 針對失敗的腳本進行重跑 """
        if not self.retry_list:
            print("  [Pass] Success。")
            return

        print("\n" + "=" * 50)
        print("          開始執行 Retry (重跑失敗項目)")
        print("=" * 50)
        print(f"  待重跑腳本數: {len(self.retry_list)}")

        for script_name, errors in self.retry_list.items():
            print(f"\n  [Retry] >>> 正在重跑: {script_name}")
            print(f"          (先前失敗原因: {errors})")

            script_path = os.path.join(self.base_dir, script_name)

            if not os.path.exists(script_path):
                print(f"  [Error] 找不到檔案: {script_path}，跳過。")
                continue

            # 執行重跑
            # 注意：這裡我們不使用 >> log，而是直接印在螢幕上讓使用者看重跑結果
            # 或者是您可以選擇 append 到 log: stdout=open(self.log_path, 'a')
            try:
                # 這裡選擇將輸出同時顯示並追加到 Log (如果需要)
                subprocess.run(["python", script_path], shell=True)
            except Exception as e:
                print(f"  [Retry] 執行失敗: {e}")

            time.sleep(2)  # 緩衝

        print("\n" + "=" * 50)
        print("          Retry 流程結束")
        print("=" * 50)


if __name__ == "__main__":
    manager = RetryManager()
    manager.analyze_log()
    manager.execute_retry()