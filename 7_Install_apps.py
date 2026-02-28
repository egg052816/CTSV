from auto import CtsVerifier
import os
import subprocess
import argparse
import json

class InstallApps(CtsVerifier):
    test_mapping ={
        "Instant Apps Notification Test": "install_apps_notification_test",
        "Instant Apps Recents Test": "install_apps_recents_test",
        #"View/Delete Instant Apps Test": "view_delete_instant_apps_test"
    }


    def install_apps_notification_test(self):

        self.test_name = "Instant Apps Notification Test"

        try:
            if not self.scroll_and_click(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                return False

            self.d.open_notification()
            if self.d(text="Clear all").wait(1):
                self.d(text="Clear all").click()
                print("  [Clean] 已清除通知")

            self.open_ctsv_from_recents()

            base_dir = r"D:\Python\CTSV\Downloads\android-cts-verifier"
            apk_name = "CtsVerifierInstantApp.apk"

            apk_path = os.path.join(base_dir, apk_name)

            if not os.path.exists(apk_path):
                print(f"  [Fail] 找不到 APK 檔案: {apk_path}")
                self.go_back_to_list()
                return False

            print(f"  [Install] 正在安裝: {apk_path}")

            cmd = f'adb -s {self.d.serial} install -r --instant "{apk_path}"'
            proc = subprocess.Popen(
                cmd, shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # === UI 救援階段（只處理 UI，不等 adb）===
            install_clicked = False
            for _ in range(15):  # 最多等 15 秒
                if self.d(textContains="This app was built for an older version").exists():
                    print("  [Warn] 偵測到 Play Protect 阻擋")

                    if self.d(text="More details").exists():
                        self.d(text="More details").click()
                        print("    -> 點擊 More details")
                        self.d.sleep(1)

                    install_target = self.d(textContains="Install anyway")
                    if install_target.wait(timeout=1):
                        print("    -> 點擊 Install anyway (偏移點擊左下角)")
                        install_target.click(offset=(0.1, 0.9))
                        install_clicked = True
                        break

            self.d.sleep(1)

            if not install_clicked:
                print("  [Info] 未出現 Install anyway（可能未被阻擋或已自動通過）")

            # === 現在才等 adb install 真正結束 ===
            try:
                stdout, stderr = proc.communicate(timeout=30)
                print("  [Setup] adb install 完成")
                if proc.returncode != 0:
                    print(f"  [Fail] adb install 失敗:\n{stderr.decode()}")
                    self.go_back_to_list()
                    return False
            except subprocess.TimeoutExpired:
                print("  [Fail] adb install 卡住（Play Protect 未解除）")
                proc.kill()
                self.go_back_to_list()
                return False

            # === CTS Verifier Start ===
            if not self.d(resourceId="com.android.cts.verifier:id/start_test_button").wait(timeout=5):
                print("  [Fail] 未出現 Start Test 按鈕")
                self.go_back_to_list()
                return False

            self.d(resourceId="com.android.cts.verifier:id/start_test_button").click()
            print("  [Check] 點擊 Start Test")

            if not self.d(text="Hello, World!").wait(timeout=5):
                print("  [Fail] Instant App 未成功啟動")
                self.click_fail()
                return False

            print("  [Check] Instant App 啟動成功")

            # === Notification 驗證 ==
            self.d.open_notification()
            self.d.sleep(2)

            notif_text = "Sample Instant App for Testing running"
            if not self.d(text=notif_text).exists():
                print("  [Fail] 未出現 Instant App Notification")
                self.go_back_to_list()
                return False

            self.d(text=notif_text).click()
            self.d.sleep(1)

            if self.d(text="Go to browser").exists():
                self.d(text="Go to browser").click()

            if self.d(resourceId="com.android.chrome:id/fre_icon").wait(timeout=5):
                print("  [Check] 成功跳轉至 Chrome")

            self.open_ctsv_from_recents()

            if self.d(resourceId="com.android.cts.verifier:id/pass_button", enabled=True).exists():
                self.click_pass()
            else:
                self.click_fail()

        except Exception as e:

            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    def install_apps_recents_test(self):
        self.test_name = "Instant Apps Recents Test"

        try:
            if not self.scroll_and_click(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                return False

            base_dir = r"D:\Python\CTSV\Downloads\android-cts-verifier"
            apk_name = "CtsVerifierInstantApp.apk"

            apk_path = os.path.join(base_dir, apk_name)

            if not os.path.exists(apk_path):
                print(f"  [Fail] 找不到 APK 檔案: {apk_path}")
                self.go_back_to_list()
                return False

            print(f"  [Install] 正在安裝: {apk_path}")

            cmd = f'adb -s {self.d.serial} install -r --instant "{apk_path}"'
            proc = subprocess.Popen(
                cmd, shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # === UI 救援階段（只處理 UI，不等 adb）===
            install_clicked = False
            for _ in range(15):  # 最多等 15 秒
                if self.d(textContains="This app was built for an older version").exists():
                    print("  [Warn] 偵測到 Play Protect 阻擋")

                    if self.d(text="More details").exists():
                        self.d(text="More details").click()
                        print("    -> 點擊 More details")
                        self.d.sleep(1)

                    install_target = self.d(textContains="Install anyway")
                    if install_target.wait(timeout=1):
                        print("    -> 點擊 Install anyway (偏移點擊左下角)")
                        install_target.click(offset=(0.1, 0.9))
                        install_clicked = True
                        break

            self.d.sleep(1)

            if not install_clicked:
                print("  [Info] 未出現 Install anyway（可能未被阻擋或已自動通過）")

            # === 現在才等 adb install 真正結束 ===
            try:
                stdout, stderr = proc.communicate(timeout=30)
                print("  [Setup] adb install 完成")
                if proc.returncode != 0:
                    print(f"  [Fail] adb install 失敗:\n{stderr.decode()}")
                    self.go_back_to_list()
                    return False
            except subprocess.TimeoutExpired:
                print("  [Fail] adb install 卡住（Play Protect 未解除）")
                proc.kill()
                self.go_back_to_list()
                return False

            # === CTS Verifier Start ===
            if not self.d(resourceId="com.android.cts.verifier:id/start_test_button").wait(timeout=5):
                print("  [Fail] 未出現 Start Test 按鈕")
                self.go_back_to_list()
                return False

            self.d(resourceId="com.android.cts.verifier:id/start_test_button").click()
            print("  [Check] 點擊 Start Test")
            self.d.sleep(1)

            if not self.d(text="Hello, World!").wait(timeout=5):
                print("  [Fail] Instant App 未成功啟動")
                self.click_fail()
                return False
            self.d.sleep(1)
            print("  [Check] Instant App 啟動成功")

            self.switch_to_app_via_recents("Sample Instant App for Testing")
            self.d.sleep(2)

            if not self.d(text="Hello, World!").wait(timeout=5):
                print("  [Fail] apk 未能正常顯示")
                self.click_fail()
                return False

            self.open_ctsv_from_recents()

            if self.d(resourceId="com.android.cts.verifier:id/pass_button", enabled=True).exists():
                self.click_pass()
            else:
                self.click_fail()

        except Exception as e:

            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    def view_delete_instant_apps_test(self):
        self.test_name = "View/Delete Instant Apps Test"

        try:
            if not self.scroll_and_click(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                return False

            base_dir = r"D:\Python\CTSV\Downloads\android-cts-verifier"
            apk_name = "CtsVerifierInstantApp.apk"

            apk_path = os.path.join(base_dir, apk_name)

            if not os.path.exists(apk_path):
                print(f"  [Fail] 找不到 APK 檔案: {apk_path}")
                self.go_back_to_list()
                return False

            print(f"  [Install] 正在安裝: {apk_path}")

            cmd = f'adb -s {self.d.serial} install -r --instant "{apk_path}"'
            proc = subprocess.Popen(
                cmd, shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # === UI 救援階段（只處理 UI，不等 adb）===
            install_clicked = False
            for _ in range(15):  # 最多等 15 秒
                if self.d(textContains="This app was built for an older version").exists():
                    print("  [Warn] 偵測到 Play Protect 阻擋")

                    if self.d(text="More details").exists():
                        self.d(text="More details").click()
                        print("    -> 點擊 More details")
                        self.d.sleep(1)

                    install_target = self.d(textContains="Install anyway")
                    if install_target.wait(timeout=1):
                        print("    -> 點擊 Install anyway (偏移點擊左下角)")
                        install_target.click(offset=(0.1, 0.9))
                        install_clicked = True
                        break

            self.d.sleep(1)

            if not install_clicked:
                print("  [Info] 未出現 Install anyway（可能未被阻擋或已自動通過）")

            # === 現在才等 adb install 真正結束 ===
            try:
                stdout, stderr = proc.communicate(timeout=30)
                print("  [Setup] adb install 完成")
                if proc.returncode != 0:
                    print(f"  [Fail] adb install 失敗:\n{stderr.decode()}")
                    self.go_back_to_list()
                    return False
            except subprocess.TimeoutExpired:
                print("  [Fail] adb install 卡住（Play Protect 未解除）")
                proc.kill()
                self.go_back_to_list()
                return False

            if not self.d(resourceId="com.android.cts.verifier:id/start_test_button").wait(timeout=5):
                print("  [Fail] 未出現 Start Test 按鈕")
                self.go_back_to_list()
                return False

            is_pass = False

            self.d(resourceId="com.android.cts.verifier:id/start_test_button").click()
            print("  [Check] 點擊 Start Test")
            self.d.sleep(1)

            self.settings_nav("Apps")
            self.d(textContains="See all ").click()
            self.d.sleep(2)
            if self.d(className="android.widget.Button").wait(2):
                self.d(className="android.widget.Button").click()
            else:
                print("  [Fail] 找不到All apps 選單")
                self.open_ctsv_from_recents()
                self.click_fail()
                return False

            self.d.sleep(1)
            self.d(textContains = "Instant apps").click()

            if self.d(text="Sample Instant App for Testing").exists(3):
                self.d(text="Sample Instant App for Testing").click()
                self.d.sleep(1)
                self.d(text="Clear app").click()
                self.d.sleep(1)
                self.d.xpath('(//*[@text="Clear app"])[2]').click()

                if self.d(text = "All apps").exists(3):
                    is_pass = True
                else:
                    print("  [Fail] Clear app 點擊沒有反應")
            else:
                print("  [Fail] Instant apps 找不到 Sample Instant App for Testing")


            self.open_ctsv_from_recents()

            if is_pass and self.d(resourceId="com.android.cts.verifier:id/pass_button", enabled=True).exists():
                self.click_pass()
            else:
                self.click_fail()

        except Exception as e:

            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            safe_test_name = self.test_name.replace("/", "_")
            self.d.screenshot(f"Crash_{safe_test_name}.jpg")

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

    task = InstallApps()
    try:
        if args.retry:
            fail_list = json.loads(args.retry)
            task.run_specific_tests(fail_list)
        else:
            task.install_apps_notification_test()
            task.install_apps_recents_test()
            task.view_delete_instant_apps_test()

    finally:
        try:
            task.d.stop_uiautomator()
        except:
            pass






