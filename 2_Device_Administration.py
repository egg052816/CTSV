from auto import CtsVerifier
import uiautomator2 as u2
import subprocess
import os
import time

class DeviceAdministration(CtsVerifier):

    def failed_testcase(self):
        # failed = []
        pass

    def device_admin_tapjacking_test(self):
        test_name = "Device Admin Tapjacking Test"

        try:
            # 1. 進入測試
            if not self.scroll_and_click(test_name):return

            # 2. 點擊按鈕 (觸發遮罩)
            self.d(resourceId="com.android.cts.verifier:id/enable_admin_overlay_button").click(timeout=5)

            overlay_text = "Any security sensitive controls below should not respond to taps as long as this activity is visible."

            if self.d(textContains=overlay_text).wait(timeout=5):
                print("  [Info] 偵測到遮罩文字，開始檢查鎖定狀態...")

                self.d.sleep(0.5)

            target_ui = self.d(textContains=overlay_text)
            bounds_before = target_ui.info["bounds"]

            self.d.swipe(0.5, 0.5, 0.5, 0.1)
            self.d.sleep(1)

            bounds_after = target_ui.info["bounds"]
            is_scroll_locked = (bounds_before == bounds_after)

            self.d(description="Navigate up").click()
            self.d.sleep(0.5)

            is_pass = False
            if self.d(textContains=overlay_text).exists:
                is_pass = True

            self.d.press("back")
            self.d.press("back")

            if is_scroll_locked and is_pass :
                self.click_pass()
            else:
                self.click_fail()

        except Exception as e:
            print(f"  [Crash] {test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{test_name}.jpg")

            self.go_back_to_list()

        while self.d(text=test_name).exists() and not self.d(description="More options").exists:
            self.d.press("back")
            self.d.sleep(0.5)

    def device_admin_uninstall_test(self):
        test_name = "Device Admin Uninstall Test"

        try:
            if not self.scroll_and_click(test_name): return

            base_dir = r"D:\Python\CSTV\Downloads\android-cts-verifier"
            apk_name = "CtsEmptyDeviceAdmin.apk"

            apk_path = os.path.join(base_dir, apk_name)

            if  os.path.exists(apk_path):
                print(f"[Install] 正在安裝: {apk_path}")
                cmd = f'adb -s {self.d.serial} install -r -g "{apk_path}"'
                subprocess.run(cmd, shell=True, check=True)
                self.d.sleep(1)
            else:
                print(f"[Error] 找不到 {apk_path}")
                return

            self.d(resourceId="com.android.cts.verifier:id/enable_device_admin_button").click()

            self.d.swipe(0.5, 0.5, 0.5, 1.0)
            self.d(resourceId="com.android.settings:id/restricted_action").click()
            self.d.sleep(1)


            self.d(resourceId="com.android.cts.verifier:id/open_app_details_button").click()
            self.d.sleep(1)
            self.d(textContains="Uninstall").click()
            self.d.swipe(0.5, 0.5, 0.5, 0.2)
            self.d.sleep(1)
            self.d(resourceId="com.android.settings:id/restricted_action").click()
            self.d.sleep(1)

            if self.d(resourceId="com.android.cts.verifier:id/pass_button", enabled=True).wait(timeout=3):
                self.click_pass()
            else:
                print(f"{test_name} Failed")
                self.click_fail()

        except Exception as e:
            print(f"  [Crash] {test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{test_name}.jpg")

            self.go_back_to_list()


    def policy_serialization_test(self):
        test_name = "Policy Serialization Test"

        try:
            if not self.scroll_and_click(test_name): return

            self.d(resourceId="com.android.cts.verifier:id/generate_policy_button").click(timeout=2)
            self.d(text="Maximum Failed Passwords for Wipe").click()
            self.d(text="Maximum Time to Lock").click()
            self.d.sleep(2)
            self.d(resourceId="com.android.cts.verifier:id/apply_policy_button").click()
            self.d.sleep(2)

            serial = self.d.serial
            subprocess.run(f"adb -s {serial} reboot", shell=True)
            print("  [Wait] 手機正在重啟中...")
            subprocess.run(f"adb -s {serial} wait-for-device", shell=True)
            print("  [Wait] USB 已連線，正在等待 Android 系統啟動 (檢查 sys.boot_completed)...")

            start_time = time.time()
            boot_timeout = 120
            is_booted = False

            while time.time() - start_time < boot_timeout:
                try:
                    # 發送指令查詢系統屬性
                    # capture_output=True 可以拿到指令的回傳值
                    result = subprocess.run(
                        f"adb -s {serial} shell getprop sys.boot_completed",
                        shell=True,
                        capture_output=True,
                        text=True
                    )

                    # 檢查回傳值是否包含 "1"
                    if result.stdout.strip() == "1":
                        print(f"  [System] 系統啟動完成！(耗時: {int(time.time() - start_time)}秒)")
                        is_booted = True
                        break
                except:
                    pass  # 忽略指令失敗 (因為系統可能還沒準備好)

                # 每秒檢查一次
                time.sleep(1)

            if not is_booted:
                print("  [Error] 重開機超時，系統未在時間內回應。")
                raise Exception("Reboot Timeout")

            # 5. 第三階段：連線與緩衝
            # 雖然系統說好了，但 Launcher (桌面) 可能還在 render，給它 2 秒緩衝最保險
            time.sleep(2)

            print("  [Reconnect] 重新建立 u2 連線...")
            self.d = u2.connect(serial)


            self.d.app_start("com.android.cts.verifier")
            self.d.sleep(4)
            self.scroll_and_click(test_name)

            if self.d(resourceId="com.android.cts.verifier:id/pass_button", enabled=True).wait(timeout=3):
                self.click_pass()
            else:
                print(f"{test_name} Failed")
                self.click_fail()


        except Exception as e:
            print(f"  [Crash] {test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{test_name}.jpg")

            self.go_back_to_list()

    def screen_lock_test(self):
        test_name = "Screen Lock Test"

        try:
            if not self.scroll_and_click(test_name): return

            self.set_screen_lock()
            self.d.sleep(2)

            self.d.app_start("com.android.cts.verifier")
            self.d.sleep(2)

            self.d(text="Force Lock").click()
            self.d.sleep(1)
            self.d.swipe(0.5, 0.5, 0.5, 1.0)
            self.d(resourceId="com.android.settings:id/restricted_action").click()
            self.d.sleep(3)


            self.unlock_device()

            if self.d(resourceId="com.android.cts.verifier:id/pass_button", enabled=True).wait(timeout=3):
                self.click_pass()
            else:
                print(f"{test_name} Failed")
                self.click_fail()

            self.d.sleep(1)
            self.remove_screen_lock()

        except Exception as e:
            print(f"  [Crash] {test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{test_name}.jpg")

            self.go_back_to_list()

    # def aee(self):
    #     self.remove_screen_lock()



if __name__ == "__main__":
    task = DeviceAdministration()
    task.failed_testcase()
    task.device_admin_tapjacking_test()
    task.device_admin_uninstall_test()
    task.policy_serialization_test()
    task.screen_lock_test()
    # task.aee()

