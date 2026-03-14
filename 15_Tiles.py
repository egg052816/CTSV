from auto import CtsVerifier
import argparse
import json
import subprocess
import os

class Tiles(CtsVerifier):

    test_mapping = {
        "Tile Service Request Test": "tile_service_request_test",
        "Tile Service Test" : "tile_service_test",
    }


    def tile_service_request_test(self):

        self.test_name = "Tile Service Request Test"

        try:
            if not self.scroll_and_click(self.test_name): return False

            self.d.sleep(2)

            base_dir = r"D:\Python\CTSV\Downloads\android-cts-verifier"
            apk_name = "CtsTileServiceApp.apk"

            apk_path = os.path.join(base_dir, apk_name)

            if os.path.exists(apk_path):
                print(f"  [Install] 正在安裝: {apk_path}")
                cmd = f'adb -s {self.d.serial} install -r -g "{apk_path}"'
                result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, encoding='utf-8')
                output_log = result.stdout.strip()
                self.d.sleep(1)
            else:
                print(f"  [Error] 找不到 {apk_path}")
                return False

            if "Success" in output_log:
                print("  [Check] 偵測到 'Success'，判定測試通過。")
                self.d(resourceId="com.android.cts.verifier:id/tiles_action_pass",enabled=True).click()
                self.d.sleep(2)
            else:
                # 為了防止只有 Stderr 有訊息，我們把 Stderr 也印出來
                if result.stderr:
                    print(f"  [Error Output] {result.stderr}")

                print("  [Check] 未偵測到 'Success'，判定測試失敗。")
                self.click_fail()  # 呼叫您現有的 Fail 點擊函式


            self.d.sleep(2)
            self.d.open_quick_settings()
            self.d.sleep(1)
            self.d.swipe_ext("left")

            is_massage_exist = True

            if not self.d(textContains="Request Tile Service").exists(3):
                is_massage_exist = False
            self.open_ctsv_from_recents()
            if not is_massage_exist:
                self.d(resourceId="com.android.cts.verifier:id/tiles_action_pass", enabled=True).click()
                self.d.sleep(1)
            else:
                print("  [Fail] 通知欄不應該出現有Request Tile Service")
                self.click_fail()
                return False

            self.d.sleep(1)
            start_request = self.d(resourceId="com.android.cts.verifier:id/tiles_action_request",enabled=True)

            if not start_request.wait(3):
                self.d(scrollable=True).scroll.to(resourceId="com.android.cts.verifier:id/tiles_action_request",enabled=True)
                self.d.sleep(1)
            if start_request.exists(2):
                start_request.click()
            else:
                print("  [Fail] 滾動到底部仍找不到 Start Request")
                self.click_fail()
                return False

            self.d.sleep(1)
            if self.d(className="android.widget.LinearLayout", text="Request Tile Service, On").wait(3):
                self.d.press("back")

            self.d.sleep(1)

            if not start_request.wait(3):
                self.d(scrollable=True).scroll.to(resourceId="com.android.cts.verifier:id/tiles_action_request",enabled=True)
                self.d.sleep(1)
            if start_request.exists(2):
                start_request.click()
            else:
                print("  [Fail] 滾動到底部仍找不到 Start Request")
                self.click_fail()
                return False

            self.d.sleep(2)
            massage = "CtsTileServiceApp wants to add the following tile to Quick Settings"
            is_pass = False
            if self.d(className="android.widget.LinearLayout", text="Request Tile Service, On").wait(3):
                is_massage_pass = (self.d(resourceId="com.android.systemui:id/text").info.get("text") == massage)

                if is_massage_pass:
                    is_pass = True

            self.d.sleep(1)
            self.d(text="Do not add tile").click()
            if not is_pass:
                print("  [Fail] 對話框未出現相對應的測試label名稱")
                self.click_fail()
                return False
            else:
                print("  [Check] 驗證 Do not add tile 功能正常")
                pass_btn = self.d(resourceId="com.android.cts.verifier:id/tiles_action_pass", enabled=True)

                if not pass_btn.exists(2):
                    print("  [Action] 畫面上沒看到 Pass 按鈕，嘗試往下滾動...")
                    self.d(scrollable=True).scroll.to(resourceId="com.android.cts.verifier:id/tiles_action_pass", enabled=True)
                    self.d.sleep(1)

                if pass_btn.exists(3):
                    pass_btn.click()
                    print("  [Check] 成功點擊 Pass 按鈕")
                else:
                    # 如果滾到底部還是找不到，或是按鈕一直是灰色的 (Disabled)
                    print("  [Fail] 滾到底部仍找不到 Pass 按鈕，或按鈕未亮起 (未被 Enable)")
                    self.click_fail()
                    return False

            self.d.sleep(1)

            if not start_request.exists(2):
                self.d(scrollable=True).scroll.to(resourceId="com.android.cts.verifier:id/tiles_action_request",enabled=True)
                self.d.sleep(1)
            if start_request.exists(3):
                start_request.click()
            else:
                print("  [Fail] 滾動到底部仍找不到 Start Request.")
                self.click_fail()
                return False

            self.d.sleep(1)
            if self.d(className="android.widget.LinearLayout", text="Request Tile Service, On").wait(3):
                self.d(text="Add tile").click()

            self.d.sleep(2)

            if self.add_app_tile("Request Tile Service"):
                self.open_ctsv_from_recents()
                pass_btn = self.d(resourceId="com.android.cts.verifier:id/tiles_action_pass", enabled=True)

                if not pass_btn.exists(2):
                    print("  [Action] 畫面上沒看到 Pass 按鈕，嘗試往下滾動...")
                    self.d(scrollable=True).scroll.to(resourceId="com.android.cts.verifier:id/tiles_action_pass",enabled=True)
                    self.d.sleep(1)

                if pass_btn.exists(3):
                    pass_btn.click()
                    print("  [Check] 成功點擊 Pass 按鈕")
                else:
                    # 如果滾到底部還是找不到，或是按鈕一直是灰色的 (Disabled)
                    print("  [Fail] 滾到底部仍找不到 Pass 按鈕，或按鈕未亮起 (未被 Enable)")
                    self.click_fail()
                    return False
            else:
                print("  [Fail] Quick Settings 找不到 Request Tile Service")
                self.click_fail()
                return False

            self.d.sleep(1)

            if not start_request.exists(2):
                self.d(scrollable=True).scroll.to(resourceId="com.android.cts.verifier:id/tiles_action_request",enabled=True)
                self.d.sleep(1)
            if start_request.exists(3):
                start_request.click()
            else:
                print("  [Fail] 滾動到底部仍找不到 Start Request.")
                self.click_fail()
                return False

            if self.d(resourceId="com.android.cts.verifier:id/pass_button", enabled=True).wait(7):
                self.click_pass()
            else:
                print(f"  [Fail] {self.test_name} 測試失敗")
                self.click_fail()


        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()



    def tile_service_test(self):

        self.test_name = "Tile Service Test"

        try:
            if not self.scroll_and_click(self.test_name): return False

            self.d.sleep(1)
            self.d.open_quick_settings()
            self.d.sleep(1)
            self.d.swipe_ext("left")

            if self.d(textContains="Tile Service").exists(2):
                print("  [Fail] Quick Settings 預設有 Tile Service")
                self.click_fail()
                return False
            else:
                self.open_ctsv_from_recents()
                self.d(resourceId="com.android.cts.verifier:id/tiles_action_pass", enabled=True).click()

            self.d.sleep(2)
            if self.add_app_tile("Tile Service for CTS Verifier"):
                self.open_ctsv_from_recents()
                self.d(resourceId="com.android.cts.verifier:id/tiles_action_pass", enabled=True).click()
            else:
                print("  [Fail] Quick Settings 找不到 Request Tile Service")
                self.click_fail()

            self.d.sleep(1)

            if self.d(resourceId="com.android.cts.verifier:id/pass_button", enabled=True).wait(3):
                self.click_pass()
            else:
                print(f"  [Fail] {self.test_name} 測試失敗")
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

if "__main__" == __name__:
    parser = argparse.ArgumentParser()
    parser.add_argument("--retry", type=str, help="JSON list of failed subtests")
    args = parser.parse_args()

    task = Tiles()
    try:
        if args.retry:
            fail_list = json.loads(args.retry)
            task.run_specific_tests(fail_list)
        else:
            task.tile_service_request_test()
            task.tile_service_test()

    finally:
        try:
            task.d.stop_uiautomator()
        except:
            pass







