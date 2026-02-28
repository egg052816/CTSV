from auto import CtsVerifier
import time
import json
import argparse
import subprocess

class Clock(CtsVerifier):
    class_name = "Alarms and Timers Tests"

    test_mapping = {
        "Show Alarms Test": "show_alarms_test",
        "Set Alarm Test": "set_alarm_test",
        "Start Alarm Test": "start_alarm_test",
        "Full Alarm Test": "full_alarm_test",
        "Set Timer Test": "set_timer_test",
        "Start Timer Test": "start_timer_test",
        "Start Timer With UI Test": "start_timer_with_ui_test"
    }

    def alarms_and_timers_tests(self):

        if not self.scroll_and_click(self.class_name):
            print("[Fail] 無法進入 Alarms and Timers Tests，停止測試。")
            self.go_back_to_list()

        # 依序執行測項
        time.sleep(3)
        self.show_alarms_test()
        self.set_alarm_test()
        self.start_alarm_test()
        self.full_alarm_test()
        self.set_timer_test()
        self.start_timer_test()
        self.start_timer_with_ui_test()
        self.clean_clock_data()


    def show_alarms_test(self):
        self.test_name = "Show Alarms Test"

        try:
            # 1. 進入測項
            if not self.enter_subtest(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                self.scroll_and_click(self.class_name)
                return False

            # 2. 執行該測項獨有的動作
            self.d.sleep(1)
            self.d(resourceId="com.android.cts.verifier:id/buttons").click()
            self.d.sleep(1)

            # 3. 核心判定 (驗證畫面)
            timer = self.d(resourceId = "com.google.android.deskclock:id/tab_menu_timer")
            is_passed = False
            if self.d(textContains="Alarm").wait(timeout=5) and timer.exists and self.d(resourceId="com.google.android.deskclock:id/fab").exists:
                is_passed = True
            else:
                print(f"  [Fail] {self.test_name}頁面錯誤，測試失敗")

            # 4. 收尾 (返回並打勾)
            self.open_ctsv_from_recents()  # 從 Clock App 回到 CTSV 詳細頁

            # 確保回到了有 Pass 按鈕的頁面
            if self.d(text="Show Alarms").exists:
                if is_passed:
                    self.click_pass()
                else:
                    self.click_fail()

            self.d.sleep(1)  # 緩衝一下

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    def set_alarm_test(self):
        self.test_name = "Set Alarm Test"
        self.d.watcher.stop()

        try:
            if not self.enter_subtest(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                self.scroll_and_click(self.class_name)
                return False

            time.sleep(1)
            self.d(resourceId="com.android.cts.verifier:id/buttons").click()

            is_passed = False
            clock = self.d(resourceId="com.google.android.deskclock:id/material_clock_face")
            if self.d(text="Select time").wait(5) and clock.exists and self.d(resourceId = "com.google.android.deskclock:id/material_clock_period_toggle").exists:
                is_passed = True
            else:
                print(f"  [Fail] {self.test_name}頁面錯誤，測試失敗")

            self.d.sleep(2)
            self.d(resourceId="com.google.android.deskclock:id/material_timepicker_cancel_button").click()
            self.d.sleep(1)
            self.open_ctsv_from_recents()

            if is_passed:
                self.click_pass()
            else:
                self.click_fail()

            time.sleep(1)

            self.d.watcher.start()

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")
            self.d.watcher.start()

            self.go_back_to_list()

    def start_alarm_test(self):
        self.test_name = "Start Alarm Test"

        try:
            if not self.enter_subtest(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                self.scroll_and_click(self.class_name)
                return False

            time.sleep(1)
            self.d(text="Start Alarm").click()

            is_passed = False
            alarm_is_pass = False
            alarm_is_clean = False

            time.sleep(3)
            current_app = self.d.app_current()  # 獲取當前 App 資訊
            current_pkg = current_app.get('package')

            if current_pkg == "com.android.cts.verifier" and self.d(text="Start Alarm Test").exists and self.d(
                    resourceId="com.android.cts.verifier:id/buttons").exists:
                is_passed = True

            for i in range(40):
                if self.d(text="Stop").exists:
                    self.d(text="Stop").click()
                    alarm_is_pass = True
                    break
                elif self.d(text="STOP").exists:
                    self.d(text="STOP").click()
                    alarm_is_pass = True
                    break

                # 顯示進度，讓你知道程式還活著
                print(".", end="", flush=True)
                time.sleep(3)

            print("")  # 換行

            if not alarm_is_pass:
                print(f"  [Fail] 鬧鐘計時失敗")
                self.click_fail()

            time.sleep(1)
            self.d(text="Verify").click()

            if self.d(textContains="Alarm").wait(timeout=5):
                time.sleep(2)
                if self.d(text="Start Alarm Test").exists():
                    print("  [Fail] 介面異常，不該顯示設定鬧鐘")
                else:
                    alarm_is_clean = True
                    print("  [Check] 測試正常，未顯示設定鬧鐘")
            else:
                print("  [Fail] 未跳轉至時鐘 App")

            self.open_ctsv_from_recents()

            if is_passed and alarm_is_pass and alarm_is_clean:
                self.click_pass()
            else:
                self.click_fail()

            self.d.sleep(1)

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    def full_alarm_test(self):
        self.test_name = "Full Alarm Test"

        try:
            if not self.enter_subtest(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                self.scroll_and_click(self.class_name)
                return False

            time.sleep(1)
            self.d(resourceId="com.android.cts.verifier:id/buttons").click()

            if not self.d(resourceId="com.google.android.deskclock:id/action_bar_title").wait(timeout=5):
                self.open_ctsv_from_recents()
                self.click_fail()

            self.d(scrollable=True).scroll.to(text="Create Alarm Test")
            time.sleep(1)

            target_label = "Create Alarm Test"
            target_time_part = "1:23"
            is_passed = False
            label = self.d(text=target_label).exists()
            time_set = self.d(textContains=target_time_part).exists()
            switch_on = self.d(resourceId="com.google.android.deskclock:id/onoff", checked=True).wait(5)

            print(f"  [Info] label:{label}, time_set:{time_set}, switch_on:{switch_on}")

            time.sleep(1)

            if label and time_set and switch_on:
                is_passed = True

            self.open_ctsv_from_recents()

            if is_passed:
                self.click_pass()
            else:
                self.click_fail()

            time.sleep(1)

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()


    def set_timer_test(self):
        self.test_name="Set Timer Test"

        try:
            if not self.enter_subtest(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                self.scroll_and_click(self.class_name)
                return False

            time.sleep(1)
            self.d(text="Set Timer").click()
            time.sleep(1)
            is_passed = False
            setup_time = self.d(resourceId="com.google.android.deskclock:id/timer_setup_time")
            setup_digits = self.d(resourceId = "com.google.android.deskclock:id/timer_setup_digits")

            if self.d(textContains="Timer").wait(5) and setup_time.exists and setup_digits.exists:
                is_passed = True

            self.open_ctsv_from_recents()

            if not self.d(resourceId="com.android.cts.verifier:id/fail_button").exists:
                self.open_ctsv_from_recents()

            if self.d(text=self.test_name).exists and self.d(resourceId="com.android.cts.verifier:id/buttons").exists:
                if is_passed:
                    self.click_pass()
                else:
                    self.click_fail()

            time.sleep(1)

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    def start_timer_test(self):
        self.test_name = "Start Timer Test"

        try:
            if not self.enter_subtest(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                self.scroll_and_click(self.class_name)
                return False

            time.sleep(1)
            self.d(text="Start Timer").click()

            is_passed = False
            is_notification_clean = False

            for i in range(35):
                if self.d(text="STOP").exists:
                    self.d(text="STOP").click()
                    is_passed = True
                    break
                elif self.d(text="Stop").exists:
                    self.d(text="Stop").click()
                    is_passed = True
                    break
                time.sleep(2)

            self.d.open_notification()
            time.sleep(1)

            if not self.d(text="Start Timer Test").exists:
                is_notification_clean = True

            self.open_ctsv_from_recents()


            if self.d(text=self.test_name).exists:
                if is_passed and is_notification_clean:
                    self.click_pass()
                else:
                    self.click_fail()

            time.sleep(1)

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()


    def start_timer_with_ui_test(self):
        self.test_name = "Start Timer With UI Test"

        try:
            if not self.enter_subtest(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                self.scroll_and_click(self.class_name)
                return False

            time.sleep(1)
            self.d(text="Start Timer").click()

            # 檢查是否成功跳轉到時鐘 App，並且標題正確
            # 根據 image_4bc87b.png，計時器標題應為 "Start Timer Test"
            if not self.d(text="Start Timer Test").wait(timeout=5):
                print("  [Fail] 未能啟動計時器或未跳轉至時鐘介面")
                self.click_fail()
                return False

            print("  [Check] 計時器已啟動，標題顯示正確 (Start Timer Test)")

            # === Step 3: 等待 30 秒並點擊停止 ===
            print("  [Wait] 正在等待 30 秒倒數...")

            is_timer_finished = False

            # 使用迴圈每秒檢查一次 "Stop" 按鈕是否出現
            for i in range(30):
                # 情況 A: 按鈕有文字 "Stop" 或 "STOP"
                if self.d(text="Stop").exists:
                    print(f"  [Action] 計時結束  -> 點擊 Stop")
                    self.d(text="Stop").click()
                    is_timer_finished = True
                    break
                elif self.d(text="STOP").exists:
                    print(f"  [Action] 計時結束  -> 點擊 STOP")
                    self.d(text="STOP").click()
                    is_timer_finished = True
                    break
                # 情況 B: 按鈕是圖示，檢查 content-desc (無障礙標籤)
                # 根據 Android 原生時鐘，停止按鈕通常會有 desc="Stop"
                elif self.d(description="Stop").exists:
                    print(f"  [Action] 計時結束  -> 點擊 Stop 圖示")
                    self.d(description="Stop").click()
                    is_timer_finished = True
                    break

                # 還沒響，繼續等
                if i % 5 == 0: print(f"倒數中...")
                time.sleep(1)

            if not is_timer_finished:
                self.click_fail()

            self.open_ctsv_from_recents()


            if self.d(text=self.test_name).exists and self.d(resourceId="com.android.cts.verifier:id/buttons").exists:
                self.click_pass()
            else:
                self.click_fail()

            time.sleep(1)

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    def clean_clock_data(self):
        cmd = f"adb -s {self.d.serial} shell pm clear com.google.android.deskclock"
        subprocess.run(cmd, shell=True, check=True)
        print("  [Clean] 已清除所有鬧鐘")

    def run_specific_tests(self, fail_items):
        """ 只跑失敗的 function """
        if not self.scroll_and_click(self.class_name):
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

        self.clean_clock_data()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--retry", type=str, help="JSON list of failed subtests")
    args = parser.parse_args()

    task = Clock()
    try:
        if args.retry:
            fail_list = json.loads(args.retry)
            task.run_specific_tests(fail_list)
        else:
            task.alarms_and_timers_tests()

        task.click_final_pass()

    finally:
        try:
            task.d.stop_uiautomator()
        except:
            pass
