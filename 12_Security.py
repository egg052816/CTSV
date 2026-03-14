from auto import CtsVerifier
import argparse
import json

class Security(CtsVerifier):
    test_mapping = {
        "Android Protected Confirmation Test": "android_protected_confirmation_test",
        "CA Cert install via intent": "ca_cert_install_via_intent",
        "Credential Management App Test": "credential_management_app_test",
        "Identity Credential Authentication": "identity_credential_authentication",
        "Identity Credential Authentication Multi-Document": "identity_credential_authentication_multi_document",
        "KeyChain Storage Test": "keychain_storage_test",
        "Keyguard Password Verification": "keyguard_password_verification",
        "Lock Bound Keys Test": "lock_bound_keys_test",
        "Set New Password Complexity Test": "set_new_password_complexity_test",
        # "Unlocked Device Required Keys Test": "unlocked_device_required_keys_test",
    }

    def android_protected_confirmation_test(self):

        self.test_name = "Android Protected Confirmation Test"

        try :
            if not self.scroll_and_click(self.test_name): return

            self.d.sleep(5)

            if self.d(resourceId="com.android.cts.verifier:id/pass_button", enabled=True).wait(3):
                self.click_pass()
            else:
                print(f"  [Fail] {self.test_name} 測試失敗")
                self.click_fail()

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    def ca_cert_install_via_intent(self):

        self.test_name = "CA Cert install via intent"

        try:
            if not self.scroll_and_click(self.test_name): return

            self.d.sleep(1)
            self.d(resourceId="com.android.cts.verifier:id/run_test_button").click()
            self.d.sleep(1)

            if self.d(className="android.widget.TextView",text="Install CA certificates in Settings").wait(3):
                self.d(text="Close").click()
            else:
                self.d.press("back")
                self.d.sleep(1)
                self.click_fail()
                return False

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

    def credential_management_app_test(self):

        self.test_name = "Credential Management App Test"

        try :
            if not self.scroll_and_click(self.test_name): return

            self.d.sleep(1)

            self.d(text="Request to manage credentials").click()

            app_title = self.d(resourceId="com.android.settings:id/credential_management_app_title")

            if app_title.wait(3) and self.d(resourceId="com.android.settings:id/app_details").exists():
                self.d(resourceId="com.android.settings:id/allow_button").click()
                print("  [Check] install certificates 安裝成功 ")
                self.d.sleep(1)

            credential_sub_tests = [
                "Check is credential management app",
                "Check correct authentication policy is set",
                "Generate key pair",
                "Create and install certificate",
                "Request certificate for authentication",
                "Sign data with the private key",
                "Verify signature with the public key",
                "Remove credential management app"
            ]

            for test_text in credential_sub_tests:
                print(f"\n  [Running] 正在執行: {test_text}")

                # 使用文字定位，並設定 5 秒等待超時
                target = self.d(text=test_text)

                if target.wait(timeout=3):
                    target.click()
                    self.d.sleep(1)  # 等待 UI 反應或進入下一層
                    print(f"  [Success] {test_text} 完成")
                elif self.d(scrollable=True).scroll.to(text=test_text):
                    self.d(text=test_text).click()
                    self.d.sleep(1)
                    print(f"  [Success] 滑動後找到並執行: {test_text}")
                else:
                    print(f"  [Fail] 找不到測項: {test_text}，可能需要捲動畫面或 ID 已變更")
                    return False

            if self.d(resourceId="com.android.cts.verifier:id/pass_button", enabled=True).wait(3):
                self.click_pass()
            else:
                print(f"  [Fail] {self.test_name} 測試失敗")
                self.click_fail()

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()


    def identity_credential_authentication(self):

        self.test_name = "Identity Credential Authentication"

        try :
            self.set_screen_lock()
            self.d.sleep(1)

            if not self.scroll_and_click(self.test_name): return

            self.d.sleep(2)
            self.d(resourceId="com.android.cts.verifier:id/sec_start_test_button").click()
            self.d.sleep(2)

            if self.d(resourceId="com.android.cts.verifier:id/pass_button", enabled=True).wait(3):
                self.click_pass()
            else:
                print("  [Fingerprint] 該測項需要設定指紋辨識，無法用執行自動化測試")
                self.click_fail()

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()


    def identity_credential_authentication_multi_document(self):

        self.test_name = "Identity Credential Authentication Multi-Document"

        try :
            if not self.scroll_and_click(self.test_name): return

            self.d.sleep(2)
            self.d(resourceId="com.android.cts.verifier:id/sec_start_test_button").click()
            self.d.sleep(1)

            if self.d(resourceId="com.android.cts.verifier:id/pass_button", enabled=True).wait(3):
                self.click_pass()
            else:
                print("  [Fingerprint] 該測項需要設定指紋辨識，無法用執行自動化測試")
                self.click_fail()

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

        finally:
            self.remove_screen_lock()

    def keychain_storage_test(self):

        self.test_name = "KeyChain Storage Test"

        try :
            if not self.scroll_and_click(self.test_name): return

            self.d.sleep(1)
            self.d(resourceId="com.android.cts.verifier:id/action_next").click()
            self.d.sleep(2)

            next_text = self.d(resourceId="com.android.cts.verifier:id/test_log")
            if "Reading resources" in next_text.get_text():
                self.d(resourceId="com.android.cts.verifier:id/action_next").click()
            else:
                print(f"  [Fail] {self.test_name} 測試失敗")
                self.click_fail()
                return False

            self.d.sleep(1)
            self.d(resourceId="com.android.cts.verifier:id/action_next").click()
            self.d.sleep(1)

            self.d.sleep(7)
            next_text2 = self.d(resourceId="com.android.cts.verifier:id/test_log")
            if "Requesting install of credentials" in next_text2.get_text():
                self.d(resourceId="com.android.cts.verifier:id/action_next").click()
            else:
                print(f"  [Fail] {self.test_name} 測試失敗")
                self.click_fail()
                return False

            self.d.sleep(1)
            self.d(resourceId="com.android.cts.verifier:id/action_next").click()
            self.d.sleep(1)

            if self.d(resourceId="android:id/alertTitle", text="Choose certificate").wait(3):
                self.d(text="SELECT").click()
            else:
                print(f"  [Fail] {self.test_name} 測試失敗")
                self.d.press("back")
                self.click_fail()
                return False

            self.d.sleep(2)
            next_text3 = self.d(resourceId="com.android.cts.verifier:id/test_log")
            if "Starting web server" in next_text3.get_text():
                self.d(resourceId="com.android.cts.verifier:id/action_next").click()
            else:
                print(f"  [Fail] {self.test_name} 測試失敗")
                self.click_fail()
                return False

            self.d.sleep(1)
            self.d(resourceId="com.android.cts.verifier:id/action_next").click()
            self.d.sleep(2)

            self.settings_in_nav("More security & privacy", "Encryption & credentials", "Clear credentials")

            self.d.sleep(2)

            retry_back = 0
            while not self.d(resourceId="com.android.cts.verifier:id/pass_button").exists() and retry_back < 4:
                self.d.press("back")
                self.d.sleep(1)
                retry_back += 1

            if self.d(resourceId="com.android.cts.verifier:id/pass_button", enabled=True).wait(3):
                self.click_pass()
            else:
                print(f"  [Fail] {self.test_name} 測試失敗")
                self.click_fail()

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    def keyguard_password_verification(self):

        self.test_name = "Keyguard Password Verification"

        try:
            if not self.scroll_and_click(self.test_name): return

            self.remove_screen_lock()

            self.d.sleep(1)
            self.d(resourceId="com.android.cts.verifier:id/lock_set_btn").click()
            if self.d(resourceId="com.android.settings:id/app_bar").wait(3) and self.d(text="Continue without fingerprint").exists:
                self.d(text="Continue without fingerprint").click()
            self.d.sleep(2)
            self.d(text="Pattern").click()
            if self.d(resourceId="com.android.settings:id/lockPattern").wait(3):
                print("  [Check] Confirm your pattern")
                self._draw_l_shape_pattern()  # 第一次
                self.d(text="Next").click()
                self.d.sleep(1)
                self._draw_l_shape_pattern()  # 第二次
                self.d(text="Confirm").click()
                if self.d(text="Done").wait(3):
                    self.d(text="Done").click()

                print(f"  [Security] 設定密碼完成")
            else:
                self.d.press("back")
                print("  [Fail] 無法設定密碼，測試失敗")
                self.click_fail()

            if self.d(resourceId="com.android.cts.verifier:id/lock_change_btn").wait(3):
                print("  [Check] 驗證 Change password")
                self.d(resourceId="com.android.cts.verifier:id/lock_change_btn").click()
            else:
                self.d.press("back")
                print(f"  [Fail] {self.test_name} 測試失敗")
                self.click_fail()

            self.d.sleep(1)
            self._draw_l_shape_pattern()

            if self.d(resourceId="com.android.settings:id/app_bar").wait(3) and self.d(text="Continue without fingerprint").exists:
                self.d(text="Continue without fingerprint").click()
            self.d.sleep(2)
            self.d(text="None").click()
            if self.d(resourceId="com.android.settings:id/scrollView").wait(3):
                print("  [Check] 刪除密碼")
                self.d(text="Delete").click()

                print(f"  [Security] 設定密碼完成")
                self.d.sleep(1)
            else:
                self.d.press("back")
                print("  [Fail] 無法更改密碼，測試失敗")
                self.click_fail()

            if self.d(resourceId="com.android.cts.verifier:id/pass_button", enabled=True).wait(3):
                self.click_pass()
            else:
                print(f"  [Fail] {self.test_name} 測試失敗")
                self.click_fail()

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    def lock_bound_keys_test(self):

        if self.os_version == 15:
            self.test_name = "LSKF Bound Keys Test"
        else:
            # A14 或其他舊版本預設
            self.test_name = "Lock Bound Keys Test"

        self.set_screen_lock()

        try:
            if not self.scroll_and_click(self.test_name): return

            self.d.sleep(1)


            self.d(resourceId="com.android.cts.verifier:id/sec_start_test_button").click()

            pattern_view = self.d(resourceId="com.android.systemui:id/lockPattern")
            if pattern_view.wait(10):
                info = pattern_view.info['bounds']
                left, top, right, bottom = info['left'], info['top'], info['right'], info['bottom']
                w = right - left
                h = bottom - top

                # 定義點 (1->4->7->8->9)
                p1 = (left + w / 6, top + h / 6)
                p4 = (left + w / 6, top + h / 2)
                p7 = (left + w / 6, top + 5 * h / 6)
                p8 = (left + w / 2, top + 5 * h / 6)
                p9 = (left + 5 * w / 6, top + 5 * h / 6)

                self.d.swipe_points([p1, p4, p7, p8, p9], duration=0.2)


            if self.d(resourceId="com.android.cts.verifier:id/pass_button", enabled=True).wait(3):
                self.click_pass()
            else:
                print(f"  [Fail] {self.test_name} 測試失敗")
                self.click_fail()

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

        finally:
            self.remove_screen_lock()

    def set_new_password_complexity_test(self):
        self.test_name = "Set New Password Complexity Test"

        def check_lock_options(expected_states):
            # 處理 A15 可能出現的指紋跳過視窗
            if self.d(text="Continue without fingerprint").exists(timeout=3):
                self.d(text="Continue without fingerprint").click()
                self.d.sleep(1)

            options = ["None", "Swipe", "Pattern", "PIN", "Password"]
            actual_states = []

            for opt in options:
                # 取得該選項是否 enabled
                state = self.d(text=opt).info.get("enabled", False)
                actual_states.append(state)

            print(f"  [Check] 預期: {expected_states} | 實際: {actual_states}")
            return actual_states == expected_states

        try:
            if not self.scroll_and_click(self.test_name): return

            # 定義四個按鈕的 ID 與對應的預期狀態 [None, Swipe, Pattern, PIN, Password]
            test_steps = [
                ("none", [True, True, True, True, True], None),
                ("low", [False, False, True, True, True], None),
                ("medium", [False, False, False, True, True], "Must be at least 4 characters"),
                ("high", [False, False, False, True, True], "Must be at least 6 characters"),
            ]

            results = {"none": False, "low": False, "medium": False, "high": False}

            for level, expected_btns, expected_text in test_steps:
                print(f"  [Step] : {level.upper()}")

                # 1. 點擊 CTS 內的按鈕
                btn_id = f"com.android.cts.verifier:id/set_complexity_{level}_btn"
                self.d(resourceId=btn_id).click()

                # 2. 檢查選項狀態
                if check_lock_options(expected_btns):
                    if expected_text:  # Medium 與 High 需要額外檢查 Password 描述內容
                        self.d(text="Password").click()
                        desc = self.d(resourceId="com.android.settings:id/description_text").info.get("text", "")
                        if expected_text in desc:
                            results[level] = True

                        # 點了 Password 進去，要多按一次 Back 回到 CTS
                        self.d.press("back")
                    else:
                        results[level] = True

                # 3. 回到 CTS 頁面 (確保回到主測試畫面)
                # 使用 while 迴圈直到看見按鈕，比死板的按兩次 Back 更穩
                count = 0
                while not self.d(resourceId=btn_id).exists and count < 3:
                    self.d.press("back")
                    self.d.sleep(0.5)
                    count += 1

            # 最後判定
            all_pass = all(results.values())
            if all_pass and self.d(resourceId="com.android.cts.verifier:id/pass_button").wait(timeout=3):
                print(f"  [Pass] 所有測試檢查均通過: {results}")
                self.click_pass()
            else:
                print(f"  [Fail] 部分檢查失敗: {results}")
                self.click_fail()

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")
            self.d.screenshot(f"Crash_{self.test_name}.jpg")
            self.go_back_to_list()


    def unlocked_device_required_keys_test(self):

        if self.os_version == 15:
            self.test_name = "Unlocked Device Required Keys Test"
        else:
            # A14 或其他舊版本預設
            self.test_name = "Unlocked Device Required"

        try:
            if not self.scroll_and_click(self.test_name): return

            self.set_screen_lock()

            self.d.sleep(0.5)
            self.d(resourceId="com.android.cts.verifier:id/sec_start_test_button").click()
            self.d.sleep(2)
            message = "Biometric unlock has not been set up. Go to Settings -> Security to set up biometric unlock."

            if self.d(resourceId="android:id/message").info.get("text") == message:
                self.d.press("back")
                self.d.sleep(1)
                self.click_fail()
                print("  [Fingerprint] 該測項需要設定指紋辨識，無法用執行自動化測試")
                return False

            self.d.press("power")
            self.d.sleep(6)

            self.unlock_device()
            self.d.sleep(2)

            message_complete = "Test completed successfully."

            if self.d(resourceId="android:id/message").info.get("text") != message_complete:
                self.d.press("back")
                self.d.sleep(1)
                self.click_fail()
                print(f"  [Fail] {self.test_name} 解鎖功能異常，測試失敗")
                return False

            self.d.press("back")
            self.d.sleep(1)

            if self.d(resourceId="com.android.cts.verifier:id/pass_button",
                      enabled=True).wait(3):
                self.click_pass()
            else:
                print(f"  [Fail] {self.test_name} 測試失敗")
                self.click_fail()

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

        finally:
            self.remove_screen_lock()


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

    task = Security()
    try:
        if args.retry:
            fail_list = json.loads(args.retry)
            task.run_specific_tests(fail_list)
        else:
            task.android_protected_confirmation_test()
            task.ca_cert_install_via_intent()
            task.credential_management_app_test()
            task.identity_credential_authentication()
            task.identity_credential_authentication_multi_document()
            task.keychain_storage_test()
            task.keyguard_password_verification()
            task.lock_bound_keys_test()
            task.set_new_password_complexity_test()
            task.unlocked_device_required_keys_test()

    finally:
        try:
            task.d.stop_uiautomator()
        except:
            pass







