import os
import json
import subprocess
import re

class RetryManager:
    def __init__(self):
        # 取得腳本所在目錄，確保路徑正確
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.log_path = os.path.join(self.base_dir, "execution_log.txt")
        self.py_exe = os.path.join(self.base_dir, "python_311", "python.exe")
        self.retry_list = {}  # 格式: {'1_Clock.py': ['Show Alarms Test', ...]}

    def analyze_log(self):
        print("  [Retry] 正在分析 Log 以建立 Retry List")
        current_script = None
        current_subtest = None

        try:
            with open(self.log_path, "r", encoding="utf-8-sig", errors="ignore") as f:
                for line in f:
                    raw_line = line.strip()
                    lower_line = raw_line.lower()

                    # 1️⃣ 精準抓 Running 行
                    script_match = re.search(r'running\s+([a-z0-9_]+)', lower_line)

                    if script_match:
                        script_name = script_match.group(1)

                        # 避免抓到除 1~9 開頭的測項
                        if any(script_name.startswith(str(i) + "_") for i in range(1, 10)):
                            current_script = script_name
                            current_subtest = None
                        else:
                            current_script = None  # 非測項腳本，不紀錄失敗
                        continue

                    # 2️⃣ 抓子測項
                    sub_match = re.search(r'entering test:\s*(.+)', lower_line)
                    if sub_match:
                        current_subtest = raw_line[sub_match.start(1):].strip()

                    # 3️⃣ 判定失敗
                    if (
                            "[fail]" in lower_line
                            or "[crash]" in lower_line
                            or lower_line.startswith("traceback")
                    ):
                        if current_script:
                            sub_name = current_subtest or "Unknown_Crash_Point"

                            if current_script not in self.retry_list:
                                self.retry_list[current_script] = []

                            if sub_name not in self.retry_list[current_script]:
                                self.retry_list[current_script].append(sub_name)
                                print(f"    -> [Found Fail] {current_script} :: {sub_name}")

        except Exception as e:
            print(f"  [Error] 解析過程噴錯: {e}")

    def execute_retry(self):
        if not self.retry_list:
            print("  [Pass] 所有項目均通過，無需重試。")
            return

        print("\n" + "=" * 50)
        print("          開始執行精準 Retry (僅重跑失敗項目)")
        print("=" * 50)

        for script_name, fail_items in self.retry_list.items():
            print(f"\n  [Retry] >>> 正在重跑: {script_name}")
            print(f"          待測子項: {fail_items}")

            # 將失敗子項轉成 JSON 字串傳遞給參數
            items_arg = json.dumps(fail_items)
            script_path = os.path.join(self.base_dir, script_name)

            # 組裝指令，呼叫內置 Python 執行並傳入 --retry 參數
            cmd = f'"{self.py_exe}" "{script_path}" --retry "{items_arg}"'

            try:
                # 執行重跑，輸出直接印在螢幕上以便確認
                subprocess.run(cmd, shell=True)
            except Exception as e:
                print(f"  [Retry] 執行 {script_name} 失敗: {e}")


if __name__ == "__main__":
    manager = RetryManager()
    manager.analyze_log()
    manager.execute_retry()