from auto import CtsVerifier
import argparse
import json

class Other(CtsVerifier):
    test_mapping = {"Bubble Notification Tests": "bubble_notification_tests"}

    def bubble_notification_tests(self):

        self.test_name = "DisplayCutout Test"

        try :
            if not self.scroll_and_click(self.test_name): return

            if self.d(text="Got it").exists(timeout=5):
                self.d(text="Got it").click()
            else:
                pass

            self.d.sleep(1)

            content = " This test is to make sure that the area inside the safe insets from the DisplayCutout should be"

            if self.d(textContains=content).exists():
                for i in range(16):
                    self.d(text=i).click()
                print("  [Info] 邊框 0~15 已點選完成")
            else:
                self.click_fail()

            if self.d(resourceId="com.android.cts.verifier:id/pass_button",enabled=True).exists():
                self.click_pass()

            else:
                self.click_fail()
                print(f"  [Fail] {self.test_name} 結果不正確")

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

if "__main__" == __name__:
    parser = argparse.ArgumentParser()
    parser.add_argument("--retry", type=str, help="JSON list of failed subtests")
    args = parser.parse_args()

    task = Notification()
    try:
        if args.retry:
            fail_list = json.loads(args.retry)
            task.run_specific_tests(fail_list)
        else:
            task.displaycutout_test()

    finally:
        try:
            task.d.stop_uiautomator()
        except:
            pass














        self.d.sleep(1)
        i_m_done = self.d(text="I'm done", enabled=True)
        if not i_m_done.wait(1):
            self.d(scrollable=True).scroll.to(text="I'm done", enabled=True)

        if i_m_done.exists():
            i_m_done.click()
            self.d.sleep(0.5)
            self.d.press("power")

            intent_text = self.d(textContains="This page is a full screen intent")
            if intent_text.exists(10) and intent_text.info.get('visible-to-user'):
                self.d.press("home")
                self.d.sleep(2)
                if self.d(resourceId="com.android.systemui:id/lock_icon_view").exists(2) and self.d(
                        resourceId="com.android.systemui:id/lock_icon_view").info.get('visible-to-user'):
                    self.unlock_device()
                self.d.sleep(1)
                self.open_ctsv_from_recents()
                pass_btn = self.d(resourceId="com.android.cts.verifier:id/iva_action_button_pass", enabled=True)
                if pass_btn.exists:
                    print("  [Check] full screen intent 驗證正常")
                    self.d.sleep(1)
                    pass_btn.click()
                else:
                    print("  [Fail] full screen intent 驗證失敗")
                    self.click_fail()
                    return False
        else:
            print("  [Fail] 畫面上未顯示I'm done 按鈕可點擊，測試失敗")
            self.d.press("back")
            self.d.sleep(1)
            self.unlock_device()
            self.d.sleep(1)
            self.click_fail()
            return False

        retry_back = 0
        while not self.d(resourceId=self.btn_pass).exists() and retry_back < 2:
            self.d.press("back")
            self.d.sleep(1)
            retry_back += 1








































