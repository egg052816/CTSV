from auto import CtsVerifier
import os
import subprocess

class InstallApps(CtsVerifier):
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

            if self.d(resourceId="com.android.cts.verifier:id/pass_button").exists():
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

            if self.d(resourceId="com.android.cts.verifier:id/pass_button").exists():
                self.click_pass()
            else:
                self.click_fail()

        except Exception as e:

            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    # def view_delete_instant_apps_test(self):
    #     self.test_name = "View/Delete Instant Apps Test"




if __name__ == "__main__":
    task = InstallApps()
    task.install_apps_notification_test()
    # task.install_apps_recents_test()




