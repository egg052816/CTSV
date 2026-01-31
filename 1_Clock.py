from auto import CtsVerifier
import time

class Clock(CtsVerifier):

    def alarms_and_timers_tests(self):

        if not self.scroll_and_click("Alarms and Timers Tests"):
            print("[Fail] 無法進入 Alarms and Timers Tests，停止測試。")
            return

            # 教學彈窗點擊ok
        if self.d(text="OK").wait(timeout=3):
            print("  [Info] 偵測到說明彈窗，嘗試關閉...")
            self.d(text="OK").click()

            # 檢查有沒有第一個測項 Show Alarms Test
        if not self.d(text="Show Alarms Test").wait(timeout=3):
            print("[Fail]沒看到子選單，停止測試。")
            return

        # 依序執行測項
        self.show_alarms_test()
        self.set_alarm_test()
        self.start_alarm_test()
        self.full_alarm_test()
        self.set_timer_test()
        self.start_timer_test()
        self.start_timer_with_ui_test()
        print("=== All CLOCK Tests Finished ===")


    def show_alarms_test(self):
        test_name = "Show Alarms Test"

        # 1. 進入測項
        if not self.enter_subtest(test_name): return

        # 2. 執行該測項獨有的動作
        self.d(resourceId="com.android.cts.verifier:id/buttons").click()

        # 3. 核心判定 (驗證畫面)
        is_passed = False
        if self.d(text="Alarms").wait(timeout=5) and self.d(text="Timers").exists and self.d(resourceId="com.google.android.deskclock:id/fab").exists:
            is_passed = True
        else:
            self.click_fail()

        # 4. 收尾 (返回並打勾)
        self.d.press("back")  # 從 Clock App 回到 CTSV 詳細頁

        # 確保回到了有 Pass 按鈕的頁面
        if self.d(text="Show Alarms").exists:
            if is_passed:
                self.click_pass()
            else:
                self.click_fail()

        time.sleep(1)  # 緩衝一下


    def set_alarm_test(self):
        test_name = "Set Alarm Test"
        if not self.enter_subtest(test_name): return

        self.d(resourceId="com.android.cts.verifier:id/buttons").click()

        is_passed = False
        if self.d(text="Select time").wait(timeout=5) and self.d(resourceId="com.google.android.deskclock:id/material_clock_face").exists and self.d(resourceId = "com.google.android.deskclock:id/material_clock_period_toggle").exists:
            is_passed = True
        else:
            self.click_fail()

        self.d.press("back")
        self.d.press("back")

        if self.d(text="Set Alarm").exists:
            if is_passed:
                self.click_pass()
            else:
                self.click_fail()

        time.sleep(1)


    def start_alarm_test(self):
        test_name = "Start Alarm Test"
        if not self.enter_subtest(test_name): return

        self.d(text="Start Alarm").click()

        is_passed = False
        alarm_is_pass = False
        alarm_is_clean = False

        time.sleep(3)
        current_app = self.d.app_current()  # 獲取當前 App 資訊
        current_pkg = current_app.get('package')

        if current_pkg == "com.android.cts.verifier" and self.d(text="Start Alarm Test").exists and self.d(resourceId="com.android.cts.verifier:id/buttons").exists:
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
            self.click_fail()

        time.sleep(1)
        self.d(text="Verify").click()

        if self.d(text="Alarms").wait(timeout=5):
            if not self.d(text=test_name).exists:
                alarm_is_clean = True
            else:
                self.click_fail()
        else:
            self.click_fail()

        self.d.press("back")
        time.sleep(1)

        if is_passed and alarm_is_pass and alarm_is_clean:
            self.click_pass()
        else:
            self.click_fail()

        time.sleep(1)


    def full_alarm_test(self):
        test_name = "Full Alarm Test"
        if not self.enter_subtest(test_name): return

        self.d(text="Create Alarm").click()

        if not self.d(text="Alarms").wait(timeout=5):
            self.d.press("back")
            self.click_fail()

        target_label = "Create Alarm Test"
        target_time_part = "1:23"
        is_passed = False
        label = self.d(text=target_label).exists
        time_set = self.d(textContains=target_time_part).exists
        switch_on = self.d(resourceId="com.google.android.deskclock:id/onoff", checked=True).exists

        if label and time_set and switch_on:
            is_passed = True

        self.d.press("back")
        time.sleep(1)

        if self.d(text=test_name).exists:
            if is_passed:
                self.click_pass()
            else:
                self.click_fail()

        time.sleep(1)


    def set_timer_test(self):
        test_name = "Set Timer Test"
        if not self.enter_subtest(test_name): return

        self.d(text="Set Timer").click()
        is_passed = False

        if self.d(text="Timers").wait(timeout=5) and self.d(resourceId="com.google.android.deskclock:id/timer_setup_time").exists and self.d(text="World Clock").exists:
            is_passed = True

        self.d.press("back")
        time.sleep(1)
        if not self.d(resourceId="com.android.cts.verifier:id/fail_button").exists:
            self.d.press("back")
            time.sleep(1)


        if self.d(text=test_name).exists and self.d(resourceId="com.android.cts.verifier:id/buttons").exists:
            if is_passed:
                self.click_pass()
            else:
                self.click_fail()

        time.sleep(1)


    def start_timer_test(self):
        test_name = "Start Timer Test"
        if not self.enter_subtest(test_name): return

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

        self.d.press("back")
        time.sleep(1)

        if self.d(text=test_name).exists:
            if is_passed and is_notification_clean:
                self.click_pass()
            else:
                self.click_fail()

        time.sleep(1)


    def start_timer_with_ui_test(self):
        test_name = "Start Timer With UI Test"
        if not self.enter_subtest(test_name): return

        self.d(text="Start Timer").click()

        # 檢查是否成功跳轉到時鐘 App，並且標題正確
        # 根據 image_4bc87b.png，計時器標題應為 "Start Timer Test"
        if not self.d(text="Start Timer Test").wait(timeout=5):
            print("  [Fail] 未能啟動計時器或未跳轉至時鐘介面")
            self.click_fail()
            return

        print("  [Check] 計時器已啟動，標題顯示正確 (Start Timer Test)")

        # === Step 3: 等待 30 秒並點擊停止 ===
        print("  [Wait] 正在等待 30 秒倒數結束...")

        is_timer_finished = False

        # 使用迴圈每秒檢查一次 "Stop" 按鈕是否出現
        for i in range(30):
            # 情況 A: 按鈕有文字 "Stop" 或 "STOP"
            if self.d(text="Stop").exists:
                print(f"  [Action] 計時結束 (第 {i} 秒) -> 點擊 Stop")
                self.d(text="Stop").click()
                is_timer_finished = True
                break
            elif self.d(text="STOP").exists:
                print(f"  [Action] 計時結束 (第 {i} 秒) -> 點擊 STOP")
                self.d(text="STOP").click()
                is_timer_finished = True
                break
            # 情況 B: 按鈕是圖示，檢查 content-desc (無障礙標籤)
            # 根據 Android 原生時鐘，停止按鈕通常會有 desc="Stop"
            elif self.d(description="Stop").exists:
                print(f"  [Action] 計時結束 (第 {i} 秒) -> 點擊 Stop 圖示")
                self.d(description="Stop").click()
                is_timer_finished = True
                break

            # 還沒響，繼續等
            if i % 5 == 0: print(f"倒數中... {30 - i if 30 - i > 0 else 0}s")
            time.sleep(1)

        if not is_timer_finished:
            self.click_fail()

        self.d.press("back")
        time.sleep(1)

        if self.d(text=test_name).exists and self.d(resourceId="com.android.cts.verifier:id/buttons").exists:
            self.click_pass()
        else:
            self.click_fail()

        time.sleep(1)

if __name__ == "__main__":
    task = Clock()
    task.alarms_and_timers_tests()
    task.click_final_pass()