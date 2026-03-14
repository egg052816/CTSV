import os
import json
import subprocess
import re
import importlib.util
from datetime import datetime

class RetryManager:
    def __init__(self):
        # 取得腳本所在目錄，確保路徑正確
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.log_path = os.path.join(self.base_dir, "execution_log.txt")
        self.py_exe = os.path.join(self.base_dir, "python_311", "python.exe")
        self.retry_list = {}  # 格式: {'1_Clock.py': ['Show Alarms Test', ...]}

    def _log_message(self, message):
        """將訊息同時印在螢幕上並存入 Log"""
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        formatted_msg = f"{timestamp} {message}\n"
        print(message)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(formatted_msg)

    def get_valid_mapping(self, script_name):
        """利用您在各模組定義的 test_mapping 來驗證"""
        try:
            path = os.path.join(self.base_dir, script_name)
            spec = importlib.util.spec_from_file_location("module.name", path)
            foo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(foo)
            for attr in dir(foo):
                cls = getattr(foo, attr)
                if isinstance(cls, type) and hasattr(cls, 'test_mapping'):
                    return cls.test_mapping
        except:
            pass
        return {}

    def analyze_log(self):
        print("  [Retry] 正在分析 Log 以建立 Retry List")

        if not os.path.exists(self.log_path):
            print("  [Error] 找不到 execution_log.txt")
            return

        final_status = {}
        current_script = None
        current_subtest = None

        with open(self.log_path, "r", encoding="utf-8-sig", errors="ignore") as f:
            for line in f:
                raw_line = line.strip()
                lower_line = raw_line.lower()

                # 1. 定位腳本 (來自 Batch 的 [Running] 標籤)
                script_match = re.search(r'\[running\]\s+([\w\d_]+\.py)', lower_line)
                if script_match:
                    current_script = script_match.group(1)
                    current_subtest = None
                    continue

                # 2. 定位子項名稱
                case_match = re.search(r"\[TestCase\]\s+(?:Found|Searching for)\s*[:\s]*'?([^']+)'?", raw_line, re.I)
                if case_match:
                    current_subtest = case_match.group(1).strip()

                # 3. 記錄狀態 (以最後出現的紀錄為準)
                if current_script:
                    # 如果沒抓到 subtest 但報錯了，通常是整個腳本崩潰
                    sub_name = current_subtest if current_subtest else "FULL_RETRY"
                    key = (current_script, sub_name)

                    if "[pass]" in lower_line:
                        final_status[key] = "PASS"
                    elif "[fail]" in lower_line or "[crash]" in lower_line or "traceback" in lower_line:
                        # 只有在目前不是 PASS 的情況下才設為 FAIL
                        if final_status.get(key) != "PASS":
                            final_status[key] = "FAIL"

        # 整理出需要 Retry 的清單
        for (script, subtest), status in final_status.items():
            if status == "FAIL":
                if script not in self.retry_list:
                    self.retry_list[script] = []
                self.retry_list[script].append(subtest)
                print(f"    -> [Detected] {script} :: {subtest}")

    def execute_retry(self):
        if not self.retry_list:
            print("  [Pass] 所有項目均通過，無需重試。")
            return

        print("\n" + "=" * 50)
        print("          開始執行 Retry ")
        print("=" * 50)

        for script_name, fail_items in self.retry_list.items():
            print(f"\n  [Retry] >>> 正在重跑: {script_name}")
            print(f"          待測子項: {fail_items}")

            # 將失敗子項轉成 JSON 字串傳遞給參數
            items_arg = json.dumps(fail_items)
            script_path = os.path.join(self.base_dir, script_name)

            # 【核心修正】不使用字串拼接，改用 List 陣列來傳遞指令
            cmd_list = [self.py_exe, script_path, "--retry", items_arg]

            try:
                # 【核心修正】直接傳入 cmd_list，並移除 shell=True
                # 這樣能徹底避開 Windows CMD 的引號與空格解析錯誤
                subprocess.run(cmd_list)
            except Exception as e:
                print(f"  [Retry] 執行 {script_name} 失敗: {e}")


if __name__ == "__main__":
    manager = RetryManager()
    manager.analyze_log()
    manager.execute_retry()