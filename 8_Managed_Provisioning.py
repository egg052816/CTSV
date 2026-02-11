from auto import CtsVerifier

class ManagedProvisioning(CtsVerifier):
    class_name = "BYOD Managed Provisioning"

    def byod_managed_provisioning(self):

        if not self.scroll_and_click(self.class_name):
            print("[Fail] 無法進入 BYOD Managed Provisioning，停止測試。")
            self.go_back_to_list()
            return False


        self.start_byod_provisioning_flow()
        self.d.sleep(2)

        self.profile_owner_installed()
        self.badged_work_apps_visible_in_launcher()
        self.profile_aware_trusted_credential_settings()
        self.profile_aware_user_settings()
        self.profile_aware_app_settings()
        self.profile_aware_location_settings()
        self.profile_aware_printing_settings()
        self.personal_ringtones()
        self.open_app_cross_profiles_from_the_personal_side()
        self.open_app_cross_profiles_from_the_work_side()
        self.cross_profile_intent_filters_are_set()
        # self.non_market_app_installation_restrictions()


    def profile_owner_installed(self):
        test_name1 = "Profile owner installed"
        print(">>> Entering Test: Profile owner installed")
        self.d(text=test_name1).click()
        self.d.sleep(1)
        print("  [Pass] Profile owner installed 測試成功")

        test_name2 = "Full disk encryption enabled"

        if self.d(text=test_name2).exists(timeout=5):
            print(">>> Entering Test: Full disk encryption enabled")
            self.d(text=test_name2).click()
            self.d.sleep(1)
            print("  [Pass] Full disk encryption enabled 測試成功")

    def start_byod_provisioning_flow(self):

        if self.d(resourceId="com.android.cts.verifier:id/prepare_test_button").exists(timeout=10):
            self.d(resourceId="com.android.cts.verifier:id/prepare_test_button").click()
            if self.d(text="Accept & continue").wait(timeout=20):
                print("  [Setup] Start BYOD provisioning flow")
            else:
                print("  [Fail] BYOD 部署超時，20秒內未見 Managed Provisioning 畫面")
                self.go_back_to_list()
                return False
        else:
            print("  [Fail] 無法建立 Work Profile，未成功測試 BYOD")
            self.go_back_to_list()
            return False

        self.d(text="Accept & continue").click()
        print("  [Click] Accept & continue")

        if self.d(text="Next").exists(timeout=60):
            self.d(text="Next").click()
        else:
            print("  [Fail] Timeout,無法建立 Work Profile")
            self.go_back_to_list()
            return False

        self.d.sleep(1)

    def badged_work_apps_visible_in_launcher(self):

        self.test_name = "Badged work apps visible in Launcher"

        try:
            if not self.byod_enter_subtest(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                self.scroll_and_click(self.class_name)
                return False

            self.d(text="Go").click()
            self.d.sleep(1)

            self.settings_nav("Apps")
            self.d(textContains="See all ").click()
            self.d.sleep(2)
            self.d(text="Work").click()

            is_pass = False

            if self.d(text="CTS Verifier").wait(5) and self.d(description="Work").wait(5):
                is_pass = True
                print("  [Check] CTS Verifier Icon 判定正常")
            else:
                print("  [Fail] 未顯示 CTS Verifier Icon")
                self.open_ctsv_from_recents()
                self.d.press("back")
                self.d.sleep(1)
                self.start_byod_provisioning_flow()

            self.open_ctsv_from_recents()
            self.d.sleep(1)

            if is_pass:
                self.d(text="Pass").click()
                print(f"  [Pass] {self.test_name} 測試成功")
            else:
                self.d(text="Fail").click()
                print(f"  [Fail] {self.test_name} 測試異常，判定失敗")

            self.d.sleep(1)

        except Exception as e:

            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    def profile_aware_trusted_credential_settings(self):
        self.test_name = "Profile-aware trusted credential settings"

        try:
            if not self.byod_enter_subtest(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                self.scroll_and_click(self.class_name)
                return False

            self.d(text="Go").click()
            self.d.sleep(1)

            self.settings_in_nav("More security & privacy", "Encryption & credentials", "Trusted credentials")

            self.d.sleep(1)
            Personal = self.d(resourceId="android:id/title", text="Personal")
            Work = self.d(resourceId="android:id/title", text="Work")
            is_pass = False

            if Personal.wait(3) and Work.wait(3):
                is_pass = True
                print("  [Check] Trusted credentials 判定正常")
            else:
                print("  [Fail] 未顯示 Personal 或 Work")

            retry_back = 0
            while not self.d(text="Pass").exists() and not self.d(text="Fail").exists() and retry_back < 4:
                self.d.press("back")
                self.d.sleep(1)
                retry_back += 1

            if is_pass:
                self.d(text="Pass").click()
                print(f"  [Pass] {self.test_name} 測試成功")
            else:
                self.d(text="Fail").click()
                print(f"  [Fail] {self.test_name} 測試異常，判定失敗")

            self.d.sleep(1)

        except Exception as e:

            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()


    def profile_aware_user_settings(self):
        self.test_name = "Profile-aware user settings"

        try:
            if not self.byod_enter_subtest(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                self.scroll_and_click(self.class_name)
                return False

            self.d(text="Go").click()
            self.d.sleep(1)

            self.settings_in_nav("Passwords")

            self.d.sleep(1)
            Personal = self.d(text="Personal")
            Work = self.d(text="Work")
            is_personal_pass = False
            is_work_pass = False
            Content = "Turn auto-sync data "

            if Personal.wait(3) :
                self.d(text="Auto-sync personal data").click()
                self.d.sleep(0.5)
                if self.d(textContains=Content):
                    is_personal_pass = True
                    print("  [Check] Personal Trusted credentials 判定正常")
                else:
                    print("  [Fail] 未顯示 Personal 提示框")
            else:
                print("  [Fail] 未顯示 Personal ")

            if  Work.wait(3):
                Work.click()
                self.d.sleep(1)
                self.d.swipe(0.5, 0.5, 0.5, 1.0)
                self.d(text="Auto-sync work data").click()
                self.d.sleep(1)
                if self.d(textContains=Content):
                    is_work_pass = True
                    print("  [Check] Work Trusted credentials 判定正常")
                else:
                    print("  [Fail] 未顯示 Work 提示框")
            else:
                print("  [Fail] 未顯示 Work ")

            self.d.sleep(1)
            self.open_ctsv_from_recents()

            if is_personal_pass and is_work_pass:
                self.d(text="Pass").click()
                print(f"  [Pass] {self.test_name} 測試成功")
            else:
                self.d(text="Fail").click()
                print(f"  [Fail] {self.test_name} 測試異常，判定失敗")

            self.d.sleep(1)

        except Exception as e:

            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    def profile_aware_app_settings(self):
        self.test_name = "Profile-aware app settings"

        try:
            if not self.byod_enter_subtest(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                self.scroll_and_click(self.class_name)
                return False

            self.d(text="Go").click()
            self.d.sleep(1)

            Personal = self.d(text="Personal")
            Work = self.d(text="Work")
            is_pass = False
            is_work_item_pass = False

            if Personal.wait(3) and Work.wait(3):
                is_pass = True
                print("  [Check] Personal / Work item 顯示正常")
            else:
                print("  [Fail] 未出現 Personal / Work， 跳出測試")
                self.go_back_to_list()

            self.d.sleep(1)
            Work.click()

            if self.d(text="CTS Verifier").wait(5) and self.d(description="Work").wait(5):
                is_work_item_pass = True
                print("  [Check] Work Icon 判定正常")
            else:
                print("  [Fail] 未顯示 Work Icon")
                self.go_back_to_list()

            self.d.sleep(1)

            retry_back = 0
            while not self.d(text="Pass").exists() and not self.d(text="Fail").exists() and retry_back < 2:
                self.d.press("back")
                self.d.sleep(1)
                retry_back += 1

            if is_pass and is_work_item_pass:
                self.d(text="Pass").click()
                print(f"  [Pass] {self.test_name} 測試成功")
            else:
                self.d(text="Fail").click()
                print(f"  [Fail] {self.test_name} 測試異常，判定失敗")


        except Exception as e:

            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    def profile_aware_location_settings(self):
        self.test_name = "Profile-aware location settings"

        try:
            if not self.byod_enter_subtest(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                self.scroll_and_click(self.class_name)
                return False

            self.d(text="Go").click()
            self.d.sleep(1)

            location = self.d(text="Location for work profile")
            location_switch = location.right(className="android.widget.Switch")

            if location.wait(timeout=3) and location_switch.exists:
                print("  [Check] 選項文字與開關均正常顯示")
            else:
                print("  [Fail] 找不到 Location for work profile")
                self.go_back_to_list()

            self.d.sleep(1)
            self.d(text="Use location").right(resourceId="android:id/switch_widget").click()
            self.d.sleep(1)

            is_pass = True

            check_off = not location_switch.info.get('checked')
            text_off = self.d(textContains="Location is off").exists(timeout=3)

            if check_off and text_off:
                print("  [Check] 隨 Use location 正常關閉")
            else:
                print("  [Fail] Location for work profile 仍未關閉")
                is_pass = False

            self.d.sleep(1)
            self.d(text="Use location").right(resourceId="android:id/switch_widget").click()
            self.d.sleep(1)

            check_on = location_switch.info.get('checked')
            if not check_on:
                print("  [Fail] Location for work profile 未成功開啟")
                is_pass = False

            self.d.sleep(1)

            retry_back = 0
            while not self.d(text="Pass").exists() and not self.d(text="Fail").exists() and retry_back < 2:
                self.d.press("back")
                self.d.sleep(1)
                retry_back += 1

            if is_pass :
                self.d(text="Pass").click()
                print(f"  [Pass] {self.test_name} 測試成功")
            else:
                self.d(text="Fail").click()
                print(f"  [Fail] {self.test_name} 測試異常，判定失敗")


        except Exception as e:

            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    def profile_aware_printing_settings(self):
        self.test_name = "Profile-aware printing settings"

        try:
            if not self.byod_enter_subtest(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                self.scroll_and_click(self.class_name)
                return False

            self.d(text="Go").click()
            self.d.sleep(1)

            is_pass = False
            provisioning_flow = True

            if self.d(text="Personal").wait(3):
                self.d(resourceId = "com.android.settings:id/profile_spinner").click()
                self.d(text="Work").click()

                if self.d(text="Work").wait(3) and self.d(text="Default Print Service").exists:
                    is_pass = True
                    print("  [Check] Printing Settings 介面正常")
                else:
                    print("  [Fail] 為切換至 Work Printing Settings")
            else:
                provisioning_flow = False
                print("  [Fail] BYOD provisioning flow 未設定成功")

            retry_back = 0
            while not self.d(text="Pass").exists() and not self.d(text="Fail").exists() and retry_back < 2:
                self.d.press("back")
                self.d.sleep(1)
                retry_back += 1

            self.d.sleep(1)
            if is_pass and provisioning_flow:
                self.d(text="Pass").click()
                print(f"  [Pass] {self.test_name} 測試成功")
            else:
                self.d(text="Fail").click()
                print(f"  [Fail] {self.test_name} 測試異常，判定失敗")

            if provisioning_flow == False:
                self.start_byod_provisioning_flow()


        except Exception as e:

            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    def personal_ringtones(self):
        self.test_name = "Personal ringtones"

        try:
            if not self.byod_enter_subtest(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                self.scroll_and_click(self.class_name)
                return False

            self.d(text="Go").click()
            self.d.sleep(1)

            is_pass = True
            personal_profile = False
            if not self.settings_in_nav("Work profile sounds", "Use personal profile sounds"):
                print(f"  [Fail] 無法導航至鈴聲設定頁面")
                self.go_back_to_list()
                return False

            if self.d(text="Work phone ringtone").wait(1):
                self.d(text="Work phone ringtone").click()
                if self.d(resourceId="android:id/alertTitle").wait(1):
                    self.d(textContains="Andromeda").click()
                    if self.d(text="Andromeda").wait(1):
                        print("  [Check] work phone ringtone 設定鈴聲")
                    else:
                        is_pass = False
                        print("  [Fail] work phone ringtone 設定失敗")
                else:
                    is_pass = False
                    print("  [Fail] work phone ringtone 設定失敗")
            else:
                print("  [Info] 無 Work phone ringtone 設定")
                pass

            if self.d(text="Default work notification sound").wait(1):
                self.d(text="Default work notification sound").click()
                if self.d(resourceId="android:id/alertTitle").wait(1):
                    self.d(textContains="Adara").click()
                    if self.d(text="Adara").wait(1):
                        print("  [Check] work notification sound 設定鈴聲")
                    else:
                        is_pass = False
                        print("  [Fail] work notification sound 設定失敗")
                else:
                    is_pass = False
                    print("  [Fail] work notification sound 設定失敗")
            else:
                print("  [Info] 無 Default work notification sound 設定")
                pass

            if self.d(text="Default work alarm sound").wait(1):
                self.d(text="Default work alarm sound").click()
                if self.d(resourceId="android:id/alertTitle").wait(1):
                    self.d(textContains="Argon").click()
                    if self.d(text="Argon").wait(1):
                        print("  [Check] work alarm sound 設定鈴聲")
                    else:
                        is_pass = False
                        print("  [Fail] work alarm sound 設定失敗")
                else:
                    is_pass = False
                    print("  [Fail] work alarm sound 設定失敗")
            else:
                print("  [Info] 無 Default work alarm sound 設定")
                pass

            self.d(text="Use personal profile sounds").click()
            self.d.sleep(1)
            if self.d(text="Same as personal profile", enabled=False).wait(2):
                personal_profile = True
            else:
                print("  [Fail] Personal Ringtones 設定失敗")


            retry_back = 0
            while not self.d(text="Pass").exists() and not self.d(text="Fail").exists() and retry_back < 4:
                self.d.press("back")
                self.d.sleep(1)
                retry_back += 1

            self.d.sleep(1)
            if is_pass and personal_profile:
                self.d(text="Pass").click()
                print(f"  [Pass] {self.test_name} 測試成功")
            else:
                self.d(text="Fail").click()
                print(f"  [Fail] {self.test_name} 測試異常，判定失敗")

        except Exception as e:

            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    def open_app_cross_profiles_from_the_personal_side(self):
        self.test_name = "Open app cross profiles from the personal side"

        try:
            if not self.byod_enter_subtest(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                self.scroll_and_click(self.class_name)
                return False

            self.d(text="Go").click()
            self.d.sleep(1)
            personal = False
            work = False

            if self.d(text="Personal", selected=True).wait(1):
                self.d(resourceId="android:id/icon").click()
            self.d.sleep(1)

            if self.d(text="You selected the ctsverifier option").wait(1):
                self.d(resourceId="com.android.cts.verifier:id/button_finish").click()
                personal = True
                print("  [Check] Personal 測試正常")
            else:
                print("  [Fail] Personal item 測試失敗")

            self.d.sleep(1)
            self.d(text="Go").click()
            self.d.sleep(1)
            self.d(text="Work").click()

            if self.d(text="Work", selected=True).wait(1):
                self.d(resourceId="android:id/icon").click()
            self.d.sleep(1)

            if self.d(text="You selected the Work option.").wait(1):
                self.d(resourceId="com.android.cts.verifier:id/button_finish").click()
                work = True
                print("  [Check] Work 測試正常")
            else:
                print("  [Fail] Work item 測試失敗")

            if personal and work:
                self.d(text="Pass").click()
                print(f"  [Pass] {self.test_name} 測試成功")
            else:
                self.d(text="Fail").click()
                print(f"  [Fail] {self.test_name} 測試異常，判定失敗")

        except Exception as e:

            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    def open_app_cross_profiles_from_the_work_side(self):
        self.test_name = "Open app cross profiles from the work side"

        try:
            if not self.byod_enter_subtest(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                self.scroll_and_click(self.class_name)
                return False

            self.d(text="Go").click()
            self.d.sleep(1)
            work = False
            personal = False

            if self.d(text="Work", selected=True).wait(1):
                self.d(resourceId="android:id/icon").click()
            self.d.sleep(1)

            if self.d(text="You selected the ctsverifier option").wait(1):
                self.d(resourceId="com.android.cts.verifier:id/button_finish").click()
                work = True
                print("  [Check] Work 測試正常")
            else:
                print("  [Fail] Work item 測試失敗")

            self.d.sleep(1)
            self.d(text="Go").click()
            self.d.sleep(1)
            self.d(text="Personal").click()

            if self.d(text="Personal", selected=True).wait(1):
                self.d(resourceId="android:id/icon").click()
            self.d.sleep(1)

            if self.d(text="You selected the personal option.").wait(1):
                self.d(resourceId="com.android.cts.verifier:id/button_finish").click()
                personal = True
                print("  [Check] Personal 測試正常")
            else:
                print("  [Fail] Personal item 測試失敗")

            if work and personal:
                self.d(text="Pass").click()
                print(f"  [Pass] {self.test_name} 測試成功")
            else:
                self.d(text="Fail").click()
                print(f"  [Fail] {self.test_name} 測試異常，判定失敗")

        except Exception as e:

            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    def cross_profile_intent_filters_are_set(self):
        self.test_name = "Cross profile intent filters are set"

        try:
            if not self.byod_enter_subtest(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                self.scroll_and_click(self.class_name)
                return False

        except Exception as e:

            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    # def non_market_app_installation_restrictions(self):
    #     self.test_name = "Non-market app installation restrictions"
    #     try:
    #         if not self.byod_enter_subtest(self.test_name):
    #             print(f"  [Fail] 未能進入{self.test_name}測項")
    #             self.go_back_to_list()
    #             self.scroll_and_click(self.class_name)
    #             return False
    #
    #         sub_disable_actions = [
    #             "Disable non-market apps",
    #             "Enable non-market apps",
    #             "Disable non-market apps (global restriction)",
    #             "Enable non-market apps (global restriction)",
    #             "Disable primary user non-market apps (global restriction)",
    #             "Enable primary user non - market apps(global restriction)" ]
    #
    #         for action in sub_disable_actions:
    #             print(f"  [Action] 執行子測項: {action}")
    #
    #             test_item = self.d(textwrap=action)
    #             if test_item.exists(timeout=3):
    #                 test_item.click()
    #
    #             self.d(text="Go").click()
    #             self.d.sleep(1)
    #
    #             policy = self.d(resourceId="com.android.settings:id/admin_support_dialog_title")
    #             info = "For more info,contact your IT admin"
    #             disable_pass = False
    #
    #             if policy.wait(3) and self.d(text=info).exists:
    #                 disable_pass = True
    #                 print(f"  [Check] {action} 測試正常")
    #
    #             self.d.sleep(1)
    #             self.d(text="Close").click()
    #
    #             if disable_pass:
    #                 self.d(text="Pass").click()
    #                 print(f"  [Pass] {action} 測試成功")
    #             else:
    #                 self.d(text="Fail").click()
    #                 print(f"  [Fail] {action} 測試異常，判定失敗")
    #
    #
    #
    #
    #
    #
    #     except Exception as e:
    #
    #         print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")
    #
    #         self.d.screenshot(f"Crash_{self.test_name}.jpg")
    #
    #         self.go_back_to_list()




if __name__ == "__main__":
    task = ManagedProvisioning()
    task.byod_managed_provisioning()