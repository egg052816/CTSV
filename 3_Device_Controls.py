import os
from auto import CtsVerifier
import subprocess

class DeviceControls(CtsVerifier):
    class_name = "Controls Panel tests"

    def controls_panel_tests(self):

        if not self.scroll_and_click(self.class_name): return

        self.install_helper_app()
        self.controls_panel_visible_test()
        self.controls_panel_setting_in_extra_test_false_value()
        self.controls_panel_setting_in_extra_test_true_value()
        self.controls_panel_staring_on_keyguard_test_false_value()

    def install_helper_app(self):

        if not self.scroll_and_click(self.class_name): return

        self.test_name = "0. Install helper app"

        base_dir = r"D:\Python\CTSV\Downloads\android-cts-verifier"
        apk_name = "CtsDeviceControlsApp.apk"

        apk_path = os.path.join(base_dir, apk_name)

        try:
            if not self.enter_subtest(self.test_name): return

            if os.path.exists(apk_path):
                print(f"[Install] 正在安裝: {apk_path}")
                cmd = f'adb -s {self.d.serial} install "{apk_path}"'
                result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, encoding='utf-8')
                output_log = result.stdout.strip()
                self.d.sleep(1)

                if "Success" in output_log:
                    print("  [Check] 偵測到 'Success'，判定測試通過。")
                    self.click_pass()  # 呼叫您現有的 Pass 點擊函式
                    self.d.sleep(1)
                else:
                    # 為了防止只有 Stderr 有訊息，我們把 Stderr 也印出來
                    if result.stderr:
                        print(f"  [Error Output] {result.stderr}")

                    print("  [Check] 未偵測到 'Success'，判定測試失敗。")
                    self.click_fail()  # 呼叫您現有的 Fail 點擊函式

            else:
                print(f"[Error] 找不到 {apk_path}")
                self.click_fail()

            self.d.sleep(1)

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()


    def controls_panel_visible_test(self):

        if not self.scroll_and_click(self.class_name): return

        self.test_name = "1. Controls Panel visible test"

        try:
            if not self.enter_subtest(self.test_name): return

            self.add_device_controls_tile()
            self.d.sleep(2)

            self.d(text="Device controls").click()
            self.d.sleep(1)

            if self.d(text="Cts controls").exists(timeout=1):
                self.d(text="Cts controls").click()
            else:
                self.open_ctsv_from_recents()


            if self.d(resourceId="android:id/button1").exists(timeout=1):
                self.d(resourceId="android:id/button1").click()
            else:
                print("  [Fail] 無法按下 Add 按鈕")
                self.open_ctsv_from_recents()
                self.click_fail()
                return

            self.d.sleep(2)

            is_pass = False
            prefix_text = "This is a panel belonging to Cts controls."
            obj = self.d(textStartsWith=prefix_text)

            if obj.wait(timeout=3):
                print("  [Check] 正在驗證文字面板...")
                real_text = obj.get_text()
                if real_text and real_text.startswith(prefix_text):
                    is_pass = True
                    print("  [Check] 驗證成功：文字內容相符")
                    self.d.sleep(1)
                    self.d(resourceId="com.android.systemui:id/controls_close").click()
                else:
                    print("  [Fail] 驗證失敗：文字內容不相符")
                    self.open_ctsv_from_recents()
            self.d.sleep(1)

            self.d.open_quick_settings()
            self.d.sleep(1)

            self.d(scrollable=True).scroll.to(text="Device controls")
            self.d(text="Device controls").click()

            add_doesnt_show_again = True

            if self.d(resourceId="android:id/alertTitle").exists(timeout=2):
                add_doesnt_show_again = False
                print("  [Fail] 非首次測試，不該出現提示框")
                self.go_back_to_list()
            else:
                print(" [Check] 驗證成功:再次測試時無提示框")

            self.d(resourceId="com.android.systemui:id/controls_close").click()
            self.d.sleep(3)

            if is_pass and add_doesnt_show_again:
                self.click_pass()
            else:
                self.click_fail()

            self.d.sleep(1)

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    def controls_panel_setting_in_extra_test_false_value(self):

        if not self.scroll_and_click(self.class_name): return

        self.set_screen_lock()

        self.test_name = "2a. Controls Panel setting in extra test false value"

        try:
            if not self.enter_subtest(self.test_name): return

            self.settings_nav("Display", "Lock screen", "Use device controls")

            label = self.d(text="Use device controls")
            target_switch = label.right(className="android.widget.Switch")
            is_checked = target_switch.info['checked']
            if is_checked == False:
                print("  [Pass] 驗證成功：'Use device controls' 為關閉狀態。")
            else:
                target_switch.click()
                self.d.sleep(2)
                if target_switch.info['checked'] == False:
                    print("  [Pass] 驗證成功：已成功關閉。")
                else:
                    print("  [Fail] 嘗試關閉失敗，開關依然是開啟狀態！")
                    self.open_ctsv_from_recents()
                    self.click_fail()

            self.d.sleep(1)
            self.d.open_quick_settings()
            self.d.sleep(1)

            self.d(scrollable=True).scroll.to(text="Device controls")
            self.d(text="Device controls").click()
            self.d.sleep(1)

            is_pass = False
            expected_text = "This is a panel belonging to Cts controls. The value of the setting to act on trivial device controls from the lockscreen is false."

            if self.d(text=expected_text).exists(timeout=1):
                real_text = self.d(text=expected_text).get_text()
                if real_text == expected_text:
                    is_pass = True
                    print("  [Check] 驗證成功：文字內容相符")
                    self.d.sleep(1)
                    self.d(resourceId="com.android.systemui:id/controls_close").click()
                else:
                    self.go_back_to_list()

            self.d.sleep(1)
            self.open_ctsv_from_recents()

            if is_pass:
                self.click_pass()
            else:
                self.click_fail()

            self.d.sleep(2)

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    def controls_panel_setting_in_extra_test_true_value(self):

        if not self.scroll_and_click(self.class_name): return

        self.test_name = "2b. Controls Panel setting in extra test true value"

        try:
            if not self.enter_subtest(self.test_name): return

            self.settings_nav("Display", "Lock screen", "Use device controls")

            label = self.d(text="Use device controls")
            target_switch = label.right(className="android.widget.Switch")
            is_checked = target_switch.info['checked']
            if is_checked == True:
                print("  [Pass] 驗證成功：'Use device controls' 為開啟狀態。")
            else:
                target_switch.click()
                self.d.sleep(2)
                if target_switch.info['checked'] == True:
                    print("  [Pass] 驗證成功：已成功開啟。")
                else:
                    print("  [Fail] 嘗試關閉失敗，開關依然是關閉狀態！")
                    self.open_ctsv_from_recents()
                    self.click_fail()

            self.d.sleep(1)
            self.d.open_quick_settings()
            self.d.sleep(1)

            self.d(scrollable=True).scroll.to(text="Device controls")
            self.d(text="Device controls").click()
            self.d.sleep(1)

            is_pass = False
            expected_text = "This is a panel belonging to Cts controls. The value of the setting to act on trivial device controls from the lockscreen is true."

            if self.d(text=expected_text).exists(timeout=1):
                real_text = self.d(text=expected_text).get_text()
                if real_text == expected_text:
                    is_pass = True
                    print("  [Check] 驗證成功：文字內容相符")
                    self.d.sleep(1)
                    self.d(resourceId="com.android.systemui:id/controls_close").click()
                else:
                    self.go_back_to_list()

            self.d.sleep(1)
            self.open_ctsv_from_recents()

            if is_pass:
                self.click_pass()
            else:
                self.click_fail()

            self.d.sleep(1)

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()



    def controls_panel_staring_on_keyguard_test_false_value(self):

        if not self.scroll_and_click(self.class_name): return

        self.test_name = "3a. Control Panel starting on keyguard test false value"

        try:
            if not self.enter_subtest(self.test_name): return

            self.settings_nav("Display", "Lock screen", "Use device controls")

            label = self.d(text="Use device controls")
            target_switch = label.right(className="android.widget.Switch")
            is_checked = target_switch.info['checked']
            if is_checked == False:
                print("  [Pass] 驗證成功：'Use device controls' 為關閉狀態。")
            else:
                target_switch.click()
                self.d.sleep(2)
                if target_switch.info['checked'] == False:
                    print("  [Pass] 驗證成功：已成功關閉。")
                else:
                    print("  [Fail] 嘗試關閉失敗，開關依然是開啟狀態！")
                    self.open_ctsv_from_recents()
                    self.click_fail()

            self.d.sleep(1)
            self.d.open_quick_settings()
            self.d.sleep(1)

            self.d(scrollable=True).scroll.to(text="Device controls")
            self.d(text="Device controls").click()
            self.d.sleep(1)

            is_pass = False
            expected_text = "This value indicates the surface which the device controls panel is shown on. The current surface: Not Hosted in Dream Service"

            if self.d(resourceId="com.android.cts.devicecontrolsapp:id/surface_placeholder").exists(timeout=2):
                real_text = self.d(resourceId="com.android.cts.devicecontrolsapp:id/surface_placeholder").get_text()
                if real_text == expected_text:
                    is_pass = True
                    print("  [Check] 驗證成功：文字內容相符")
                    self.d.sleep(1)
                    self.d(resourceId="com.android.systemui:id/controls_close").click()
                else:
                    self.go_back_to_list()

            self.d.sleep(1)
            self.open_ctsv_from_recents()

            if is_pass:
                self.click_pass()
            else:
                self.click_fail()

            self.d.sleep(1)

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()



if __name__ == "__main__":
    task = DeviceControls()
    task.controls_panel_tests()
    task.click_final_pass()
    task.remove_screen_lock()