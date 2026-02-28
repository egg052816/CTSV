from auto import CtsVerifier
import argparse
import json

class Features(CtsVerifier):
    test_mapping = {
        "Capture Content For Notes Tests": "capture_content_for_notes_tests",
        "Clipboard Preview Test": "clipboard_preview_test"
    }

    def capture_content_for_notes_tests(self):

        self.test_name = "Capture Content For Notes Tests"

        try:
            if not self.scroll_and_click(self.test_name): return

            self.d.sleep(3)

            if self.d(resourceId="com.android.cts.verifier:id/pass_button",enabled = True):
                self.click_pass()
            else:
                print("  [Fail] 需要人工拿'觸控筆'操作")
                self.click_fail()

        except Exception as e:

            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()


    def clipboard_preview_test(self):

        self.test_name = "Clipboard Preview Test"

        try:
            if not self.scroll_and_click(self.test_name): return

            copy = self.d(resourceId="com.android.cts.verifier:id/clipboard_preview_test_copy")

            if copy.exists(timeout=2):
                print("  [Check] 點擊Copy ")
                copy.click()
            else:
                print("  [Fail] 未出現 Copy 按鈕 ")
                self.go_back_to_list()

            clipboard = self.d(resourceId="com.android.systemui:id/clipboard_preview")
            is_pass = False

            if clipboard.exists(timeout=2):
                print("  [Check] 點擊Clipboard ")
                clipboard.click()
                self.d.sleep(1)
                if  self.d(resourceId="com.android.systemui:id/edit_text").get_text() == "FAIL":
                    is_pass = True
                    print("  [Pass] 提示詞正確")
                else:
                    print("  [Fail] 提示詞錯誤，測試失敗")

                self.d(resourceId="com.android.systemui:id/done_button").click()
                self.d.sleep(1)

            if is_pass:
                self.click_pass()
            else:
                self.click_fail()

        except Exception as e:

            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    def run_specific_tests(self, fail_items):
        """ 只跑失敗的 function """
        if not self.scroll_and_click(self.test_name):
            return

        for item in fail_items:
            if not self.d(text=item).exists(3):
                print(f"  [Skip] 畫面上找不到測項 '{item}'，可能是 Android 版本不支援，跳過重試。")
                continue

            if item in self.test_mapping:
                func_name = self.test_mapping[item]
                print(f"  [Retry Action] 正在重跑函數: {func_name}")
                # 利用 getattr 動態呼叫函數
                getattr(self, func_name)()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--retry", type=str, help="JSON list of failed subtests")
    args = parser.parse_args()

    task = Features()
    try:
        if args.retry:
            fail_list = json.loads(args.retry)
            task.run_specific_tests(fail_list)
        else:
            task.capture_content_for_notes_tests()
            task.clipboard_preview_test()
    finally:
        try:
            task.d.stop_uiautomator()
        except:
            pass


