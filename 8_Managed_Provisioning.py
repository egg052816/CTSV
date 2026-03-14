from auto import CtsVerifier
import os
import subprocess

class ManagedProvisioning(CtsVerifier):
    class_name = "BYOD Managed Provisioning"

    def byod_managed_provisioning(self):

        if not self.scroll_and_click(self.class_name):
            print("  [Fail] 無法進入 BYOD Managed Provisioning，停止測試。")
            self.go_back_to_list()
            return False


        # Android 15 機制：獲取 Work Profile ID 並進行 adb root 提權
        if self.os_version == 15:
            print("  [Init] 版本為 Android 15，準備抓取 Work Profile ID ...")

            # 1. 查詢目前的 Work Profile User ID
            print("  [Init] 正在搜尋 Work Profile User ID...")
            cmd_list_users = f"adb -s {self.serial} shell pm list users"
            result = subprocess.run(cmd_list_users, shell=True, capture_output=True, text=True)

            self.work_user_id = None
            for line in result.stdout.splitlines():
                # Android 系統中，Work Profile 通常帶有 "Work" 字眼
                if "Work" in line or "Managed" in line:
                    try:
                        # 解析類似 "UserInfo{10:Work profile:30} running" 的字串，把 10 抓出來
                        self.work_user_id = int(line.split('{')[1].split(':')[0])
                        break
                    except (IndexError, ValueError):
                        continue

            if self.work_user_id is not None:
                print(f"  [Info] 成功抓取 Work Profile ID: u{self.work_user_id}")
                # 2. 跑 logcat 驗證 (依照您先前的 Command)
                subprocess.run(
                    f'adb -s {self.serial} logcat -d -s ActivityTaskManager | findstr /C:"START u{self.work_user_id}"',
                    shell=True)
            else:
                print("  [Warning] 目前 pm list users 尚未找到 Work Profile，ID 抓取失敗。")


        # self.start_byod_provisioning_flow()
        # self.d.sleep(2)
        #
        # self.profile_owner_installed()
        # self.badged_work_apps_visible_in_launcher()
        # self.profile_aware_trusted_credential_settings()
        # self.profile_aware_user_settings()
        # self.profile_aware_app_settings()
        # self.profile_aware_location_settings()
        # self.profile_aware_printing_settings()
        # self.personal_ringtones()
        # self.open_app_cross_profiles_from_the_personal_side()
        # self.open_app_cross_profiles_from_the_work_side()
        # self.cross_profile_intent_filters_are_set()
        # self.non_market_app_installation_restrictions()
        self.keyguard_disabled_features()
        self.vpn_test()
        self.turn_off_work_profile()

    def profile_owner_installed(self):
        test_name1 = "Profile owner installed"
        print("\n>>> Entering Test: Profile owner installed")
        self.d(text=test_name1).click()
        self.d.sleep(1)
        print("  [Pass] Profile owner installed 測試成功")

        test_name2 = "Full disk encryption enabled"

        if self.d(text=test_name2).exists(timeout=5):
            print("\n>>> Entering Test: Full disk encryption enabled")
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
            personal = self.d(resourceId="android:id/title", text="Personal")
            work = self.d(resourceId="android:id/title", text="Work")
            is_pass = False

            if personal.wait(3) and work.wait(3):
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

            self.d.sleep(1)
            self.d.app_stop("com.android.settings")  # 強制終止設定的 Lifecycle
            self.d.sleep(1)

            self.d(text="Go").click()
            self.d.sleep(1)

            self.settings_in_nav("Passwords")

            self.d.sleep(1)
            personal = self.d(text="Personal")
            work = self.d(text="Work")
            is_personal_pass = False
            is_work_pass = False

            if personal.wait(3) :
                self.d(text="Auto-sync personal data").click()
                self.d.sleep(0.5)
                if self.d(textContains="Turn auto-sync data").wait(2):
                    is_personal_pass = True
                    print("  [Check] Personal Trusted credentials 判定正常")
                else:
                    print("  [Fail] 未顯示 Personal 提示框")
            else:
                print("  [Fail] 未顯示 Personal ")

            if  work.wait(3):
                work.click()
                self.d.sleep(1)
                if self.d(scrollable=True).scroll.to(text="Auto-sync work data"):
                    self.d(text="Auto-sync work data").click()
                else:
                    print("  [Fail] Work 未顯示 Auto-sync work data")
                    self.open_ctsv_from_recents()
                    self.click_fail()

                if self.d(textContains="Turn auto-sync data").wait(2):
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

            personal = self.d(text="Personal")
            work = self.d(text="Work")
            is_pass = False
            is_work_item_pass = False

            if personal.wait(3) and work.wait(3):
                is_pass = True
                print("  [Check] Personal / Work item 顯示正常")
            else:
                print("  [Fail] 未出現 Personal / Work， 跳出測試")
                self.go_back_to_list()

            self.d.sleep(1)
            work.click()

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

            main_switch = self.d(text="Use location").right(className="android.widget.Switch")
            location = self.d(text="Location for work profile")
            location_switch = location.right(className="android.widget.Switch")
            check_off = False
            check_on = False

            if location.wait(3) and location_switch.exists:
                print("  [Check] 選項文字與開關均正常顯示")
            else:
                print("  [Fail] 找不到 Location for work profile")
                self.go_back_to_list()

            if main_switch.info.get('checked'):
                main_switch.click()
                if self.d(text="No location access").wait(5):
                    self.d(text="Close").click()

            print("  [Check] Location 已關閉，確認 Location for work profile 是否同步關閉")

            if main_switch.info.get('checked') == location_switch.info.get('checked'):
                check_off = True
            else:
                print("  [Fail] Location for work profile 開關並未隨著更改")

            main_switch.click()
            self.d.sleep(1)

            print("  [Check] Location 已開啟，確認 Location for work profile 是否同步開啟")
            if self.d(text="No location access").wait(2):
                self.d(text="Turn on location").click()
                self.d.sleep(1)

            if main_switch.info.get('checked') == location_switch.info.get('checked'):
                check_on = True
            else:
                print("  [Fail] Location for work profile 開關並未隨著更改")

            self.d.sleep(1)

            retry_back = 0
            while not self.d(text="Pass").exists() and not self.d(text="Fail").exists() and retry_back < 2:
                self.d.press("back")
                self.d.sleep(2)
                retry_back += 1

            if check_off and check_on :
                self.d(text="Pass").click()
                print(f"  [Pass] {self.test_name} 測試成功")
            else:
                self.d(text="Fail").click()
                print(f"  [Fail] {self.test_name} 測試異常，判定失敗")


        except Exception as e:

            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    # Android 15 竟然 Work Printing 頁面沒東西選
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

                if self.d(description="Work profile").wait(3):
                    is_pass = True
                    print("  [Check] Printing Settings 介面正常")
                else:
                    print("  [Fail] 未切換至 Work Printing Settings")
            else:
                provisioning_flow = False
                print("  [Fail] BYOD provisioning flow 未設定成功")

            retry_back = 0
            while not self.d(text="Pass").exists() and not self.d(text="Fail").exists() and retry_back < 2:
                self.d.press("back")
                self.d.sleep(2)
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
            if not self.settings_in_nav("Work profile sounds"):
                print(f"  [Fail] 無法導航至鈴聲設定頁面")
                self.go_back_to_list()
                return False

            work_profile_sounds = self.d(text="Use personal profile sounds")
            work_profile_sounds_switch = work_profile_sounds.right(className="android.widget.Switch")

            if work_profile_sounds_switch.info.get('checked'):
                self.d(resourceId="android:id/title", text="Use personal profile sounds").click()

            target_value_notification = self.d(text="Default work notification sound").sibling(resourceId="android:id/summary")
            target_value_alarm  = self.d(text="Default work alarm sound").sibling(resourceId="android:id/summary")

            if target_value_notification.exists:
                current_text = target_value_notification.info.get('text')
                if current_text == "None":
                    print(f"  [Check] 偵測到顯示為: {current_text}")
                else:
                    print(f"  [Fail] 數值不符，預期 None 但顯示 {current_text}")

            else:
                print("  [Info] 無 Default work notification sound 設定")
                pass


            if target_value_alarm.exists:
                current_text = target_value_alarm.info.get('text')
                if current_text == "None":
                    print(f"  [Check] 偵測到顯示為: {current_text}")
                else:
                    print(f"  [Fail] 數值不符，預期 None 但顯示 {current_text}")

            else:
                print("  [Info] 無 Default work alarm sound 設定")
                pass

            self.d(resourceId="android:id/title", text="Use personal profile sounds").click()
            if self.d(resourceId="android:id/button1").wait(3):
                self.d(resourceId="android:id/button1").click()

            self.d.sleep(1)


            if self.d(text="Same as personal profile", enabled=False).wait(2):
                personal_profile = True
                print(f"  [Check] 開啟後顯示 Same as personal profile")
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

            if not self.d(resourceId="com.android.cts.verifier:id/button_finish").exists and self.os_version == 15:

                self.d.press(61); self.d.sleep(0.5)

                self.d.press(66)

                if self.d(resourceId="android:id/contentPanel").wait(1):
                    work = True

            elif self.d(text="You selected the Work option.").wait(1):
                self.d(resourceId="com.android.cts.verifier:id/button_finish").click()
                work = True
                print("  [Check] Work 測試正常")

            else:
                print("  [Fail] Work item 測試失敗")
                self.d.press("back")

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

            if not self.d(text="Work", selected=True).exists and self.d(resourceId="android:id/icon").exists and self.os_version == 15:

                target_cmd = (f"adb -s {self.serial} shell am start --user {self.work_user_id} "
                              f"-a com.android.cts.verifier.managedprovisioning.CROSS_PROFILE_TO_WORK "
                              f"-n com.android.cts.verifier/.managedprovisioning.CrossProfileTestActivity")

                os.system(target_cmd)
                print("  [Action] 已發送強制喚醒")
                self.d.sleep(2)

                self.d.press(61); self.d.sleep(0.5)
                self.d.press(66); self.d.sleep(0.5)
                self.d.press(61); self.d.sleep(0.5)

                self.d.press(66)

                work = True

            elif self.d(text="You selected the ctsverifier option").wait(1):
                self.d(resourceId="com.android.cts.verifier:id/button_finish").click()
                work = True
                print("  [Check] Work 測試正常")

            else:
                print("  [Fail] Work item 測試失敗")
                self.d.press("back")
                self.d(text="Fail").click()


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

    def non_market_app_installation_restrictions(self):
        self.test_name = "Non-market app installation restrictions"
        try:
            if not self.byod_enter_subtest(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                self.scroll_and_click(self.class_name)
                return False

            sub_test_map = {
                "Disable non-market apps": "_disable_non_market_apps",
                "Enable non-market apps": "_enable_non_market_apps",
                "Disable non-market apps (global restriction)": "_disable_non_market_apps_global",
                "Enable non-market apps (global restriction)": "_enable_non_market_apps_global",
                "Disable primary user non-market apps (global restriction)": "_disable_primary_user_non_market_apps_global",
                "Enable primary user non-market apps (global restriction)": "_enable_primary_user_non_market_apps_global"
            }

            for action, method_name in sub_test_map.items():
                print(f"\n  [Action] 執行子測項: {action}")

                if self.d(text=action).exists(timeout=3):
                    self.d(text=action).click()
                    self.d(text="Go").click()

                    func = getattr(self, method_name, lambda x: print(f"  [Fail]找不到{method_name}"))
                    func(action)

                else:
                    print(f"  [Fail] 找不到 {action} 子測項")

            self.click_final_pass()

        except Exception as e:

            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    def _disable_non_market_apps(self, action):

        print(f"    -> [Logic] 正在執行 {action} 驗證...")
        policy = self.d(resourceId="com.android.settings:id/admin_support_dialog_title")
        info = "contact your IT admin"

        disable_pass = False

        if policy.wait(3) and self.d(resourceId="com.android.settings:id/admin_support_msg" ,textContains=info).exists:
            disable_pass = True
            print(f"  [Check] {action} 測試正常")

        self.d.sleep(1)
        self.d(text="Close").click()

        if disable_pass:
            self.d(text="Pass").click()
            print(f"  [Pass] {action} 測試成功")
        else:
            self.d(text="Fail").click()
            print(f"  [Fail] {action} 測試異常，判定失敗")

    def _enable_non_market_apps(self, action):

        print(f"    -> [Logic] 正在執行 {action} 驗證...")
        panel = self.d(resourceId="android:id/message")
        keyword_info = "allowed to install unknown apps"
        settings_btn = self.d(resourceId="android:id/button1", text="Settings")
        update_btn = self.d(resourceId="android:id/button1", text="Update")

        enable_pass = False

        self.d.press("enter"); self.d.sleep(1)

        if panel.exists(2) and self.d(textContains=keyword_info).exists:
            print("  [Check] 點擊 Setting ")
            self.d.sleep(1)
            settings_btn.click()
            self.d.sleep(2)
            self.d(text="Allow from this source").click()

        if self.d(resourceId="com.android.packageinstaller:id/install_confirm_question_update").wait(2):
            update_btn.wait(2)
            self.d.press("enter")
            self.d.sleep(1)
            update_btn.click()
            print("  [Check] 點擊 Update 安裝 app")
            self.d.sleep(1)
            if self.d(text="Install unknown apps").exists(3):
                self.d.press("back")

            if self.d(resourceId="android:id/contentPanel").wait(3) and self.d(textContains="Non-market app installation restrictions").exists:
                enable_pass = True

        else:
            retry_back = 0
            while not self.d(resourceId="com.android.cts.verifier:id/pass_button").exists() and retry_back < 5:
                self.d.press("back")
                self.d.sleep(2)
                retry_back += 1
            print("  [Fail] 未顯示 Update 提示框，判定失敗")
            return False

        if enable_pass:
            self.d(text="Pass").click()
            print(f"  [Pass] {action} 測試成功")
        else:
            self.d(text="Fail").click()
            print(f"  [Fail] {action} 測試異常，判定失敗")

    def _disable_non_market_apps_global(self, action):

        print(f"    -> [Logic] 正在執行 {action} 驗證...")
        policy = self.d(resourceId="com.android.settings:id/admin_support_dialog_title")
        info = "contact your IT admin"

        disable_pass = False

        if policy.wait(3) and self.d(resourceId="com.android.settings:id/admin_support_msg", textContains=info).exists:
            disable_pass = True
            print(f"  [Check] {action} 測試正常")

        self.d.sleep(1)
        self.d(text="Close").click()

        if disable_pass:
            self.d(text="Pass").click()
            print(f"  [Pass] {action} 測試成功")
        else:
            self.d(text="Fail").click()
            print(f"  [Fail] {action} 測試異常，判定失敗")

    def _enable_non_market_apps_global(self, action):

        print(f"    -> [Logic] 正在執行 {action} 驗證...")
        panel = self.d(resourceId="android:id/message")
        keyword_info = "allowed to install unknown apps"
        settings_btn = self.d(resourceId="android:id/button1", text="Settings")
        update_btn = self.d(resourceId="android:id/button1", text="Update")

        enable_pass = False

        self.d.press("enter"); self.d.sleep(1)

        if panel.exists(2) and self.d(textContains=keyword_info).exists:
            print(f"  [Check] 點擊 Setting 安裝 app ")
            self.d.sleep(1)
            settings_btn.click()
            self.d.sleep(2)
            self.d(text="Allow from this source").click()

        if self.d(resourceId="com.android.packageinstaller:id/install_confirm_question_update").wait(2):
            update_btn.wait(2)
            self.d.press("enter")
            self.d.sleep(1)
            update_btn.click()
            self.d.sleep(1)
            if self.d(resourceId="android:id/contentPanel").wait(2) and self.d(
                    textContains="Non-market app installation restrictions").exists:
                enable_pass = True

        elif self.d(text="Install unknown apps").exists(2):
            self.d.press("back")
            if self.d(resourceId="android:id/contentPanel").wait(2) and self.d(
                    textContains="Non-market app installation restrictions").exists:
                enable_pass = True
        else:
            retry_back = 0
            while not self.d(resourceId="com.android.cts.verifier:id/pass_button").exists() and retry_back < 5:
                self.d.press("back")
                self.d.sleep(2)
                retry_back += 1
            print("  [Fail] 未顯示 Update 提示框，判定失敗")
            return False

        if enable_pass:
            self.d(text="Pass").click()
            print(f"  [Pass] {action} 測試成功")
        else:
            self.d(text="Fail").click()
            print(f"  [Fail] {action} 測試異常，判定失敗")

    def _disable_primary_user_non_market_apps_global(self, action):

        base_dir = r"D:\Python\CTSV\Downloads\android-cts-verifier"
        apk_name = "NotificationBot.apk"

        apk_path = os.path.join(base_dir, apk_name)

        if os.path.exists(apk_path):
            print(f"  [Push] 正在上傳: {apk_path} 至 /data/local/tmp/")
            cmd = f'adb -s {self.d.serial} push "{apk_path}" /data/local/tmp/ '
            subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, encoding='utf-8')
            self.d.sleep(2)

        print(f"    -> [Logic] 正在執行 {action} 驗證...")
        policy = self.d(resourceId="com.android.settings:id/admin_support_dialog_title")
        info = "contact your IT admin"

        disable_pass = False

        if policy.wait(3) and self.d(resourceId="com.android.settings:id/admin_support_msg", textContains=info).exists:
            disable_pass = True
            print(f"  [Check] {action} 測試正常")

        self.d.sleep(1)
        self.d(text="Close").click()

        if disable_pass:
            self.d(text="Pass").click()
            print(f"  [Pass] {action} 測試成功")
        else:
            self.d(text="Fail").click()
            print(f"  [Fail] {action} 測試異常，判定失敗")

    def _enable_primary_user_non_market_apps_global(self, action):

        base_dir = r"D:\Python\CTSV\Downloads\android-cts-verifier"
        apk_name = "NotificationBot.apk"

        apk_path = os.path.join(base_dir, apk_name)

        if os.path.exists(apk_path):
            print(f"  [Push] 正在上傳: {apk_path} 至 /data/local/tmp/")
            cmd = f'adb -s {self.d.serial} push "{apk_path}" /data/local/tmp/ '
            subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, encoding='utf-8')
            self.d.sleep(2)

        print(f"    -> [Logic] 正在執行 {action} 驗證...")
        panel = self.d(resourceId="android:id/message")
        keyword_info = "allowed to install unknown apps"
        settings_btn = self.d(resourceId="android:id/button1", text="Settings")
        update_btn = self.d(resourceId="android:id/button1", text="Update")
        install_btn = self.d(resourceId="android:id/button1", text="Install")

        enable_pass = False

        if panel.exists(2) and self.d(textContains=keyword_info).exists:
            print(f"  [Check] 點擊 Setting 進入安裝頁面 ")
            self.d.sleep(1)
            settings_btn.click()
            self.d.sleep(2)

        if self.d(className="android.widget.TextView", text="Install unknown apps").exists(2):
            self.d(text="Allow from this source").click()
            print(f"  [Check] 確認是否跳出 Install unknown apps ")

        if self.d(resourceId="com.android.packageinstaller:id/install_confirm_question").exists(2):
            install_btn.click()
            print("  [Check] 點擊 Install 安裝 app ")


        if self.d(resourceId="com.android.packageinstaller:id/install_confirm_question_update").wait(2):
            update_btn.wait(2)
            self.d.press("enter")
            self.d.sleep(1)
            update_btn.click()
            self.d.sleep(4)
            if self.d(resourceId="android:id/contentPanel").wait(2) and self.d(
                    textContains="Non-market app installation restrictions").exists:
                enable_pass = True

        elif self.d(text="Install unknown apps").exists(2):
            self.d.press("back")
            if self.d(resourceId="android:id/contentPanel").wait(2) and self.d(
                    textContains="Non-market app installation restrictions").exists:
                enable_pass = True
        else:
            retry_back = 0
            while not self.d(resourceId="com.android.cts.verifier:id/pass_button").exists() and retry_back < 5:
                self.d.press("back")
                self.d.sleep(2)
                retry_back += 1
            print("  [Fail] 未顯示 Update 提示框，判定失敗")
            return False

        if enable_pass:
            self.d(text="Pass").click()
            print(f"  [Pass] {action} 測試成功")
        else:
            self.d(text="Fail").click()
            print(f"  [Fail] {action} 測試異常，判定失敗")


    def keyguard_disabled_features(self):
        self.test_name = "Keyguard disabled features"

        try:
            if not self.byod_enter_subtest(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name} 測項")
                self.go_back_to_list()
                self.scroll_and_click(self.class_name)
                return False

            self.settings_nav("Security & privacy", "More security & privacy", "Device admin apps")

            device_admin_apps = self.d(resourceId="com.android.settings:id/switchWidget")[1]

            if not device_admin_apps.info.get('checked'):
                device_admin_apps.click()

            if self.d(scrollable=True).scroll.to(resourceId="com.android.settings:id/restricted_action"):
                self.d.sleep(1)
                self.d(resourceId="com.android.settings:id/restricted_action").click()
            else:
                self.d.press("back")
                print("  [Fail] 找不到 Activate this device admin app 按鈕")
                self.click_fail()

            self.d.sleep(1)

            self.set_screen_lock()

            self.d(resourceId="com.android.cts.verifier:id/prepare_test_button").click()
            self.d.sleep(1)

            sub_test_map = {
                "Disable trust agents": "_disable_trust_agents",
                "Unredacted notifications disabled on keyguard": "_unredacted_notifications_disabled_on_keyguard"
            }

            for action, method_name in sub_test_map.items():
                print(f"\n  [Action] 執行子測項: {action}")

                if self.d(text=action).exists(timeout=3):
                    self.d(text=action).click()
                    self.d(text="Go").click()

                    func = getattr(self, method_name, lambda x: print(f"  [Fail]找不到{method_name}"))
                    func(action)

                else:
                    print(f"  [Fail] 找不到 {action} 子測項")

            retry_back = 0
            while not self.d(text="Pass").exists() and not self.d(text="Fail").exists() and retry_back < 5:
                self.d.press("back")
                self.d.sleep(1)
                retry_back += 1

            self.click_final_pass()


        except Exception as e:

            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

        finally:
            self.remove_screen_lock()



    def _disable_trust_agents(self, action):

        print(f"    -> [Logic] 正在執行 {action} 驗證...")

        self.settings_in_nav("More security & privacy", "Trust agents")

        policy = self.d(resourceId="com.android.settings:id/admin_support_dialog_title")
        info = "contact your IT admin"
        extend_unlock_btn = self.d(resourceId="android:id/title", text="Extend Unlock")

        is_pass = False

        if extend_unlock_btn.exists(2):
            print(f"  [Check] 點擊並確認 Extend Unlock ")
            extend_unlock_btn.click()
            self.d.sleep(1)

        if policy.wait(3) and self.d(resourceId="com.android.settings:id/admin_support_msg" ,textContains=info).exists:
            is_pass = True
            print(f"  [Check] {action} 測試正常")

        self.d.sleep(1)
        self.d(text="Close").click()

        while not self.d(resourceId="android:id/alertTitle").wait(1) and not self.d(resourceId="android:id/contentPanel").exists:
            self.d.press("back")

        if is_pass:
            self.d(text="Pass").click()
            print(f"  [Pass] {action} 測試成功")
        else:
            self.d(text="Fail").click()
            print(f"  [Fail] {action} 測試異常，判定失敗")

    def _unredacted_notifications_disabled_on_keyguard(self, action):

        print(f"    -> [Logic] 正在執行 {action} 驗證...")

        self.d.sleep(2)
        self.d.press("power")

        contents_hidden_btn = self.d(resourceId="android:id/title", text="Contents hidden by policy")
        contents_notification_btn = self.d(resourceId="android:id/title", text="This is a notification")

        is_pass = False
        is_notification_pass = False

        if contents_hidden_btn.exists(2):
            print(f"  [Check] 確認 Notification 是否是隱藏的 ")
            is_pass = True
            self.d.sleep(1)
        else:
            print("  [Fail] Notification 異常，測試失敗")

            self.d.unlock()
            self.d.sleep(1)
            self.d(text="Fail").click()

        self.unlock_device()

        self.d.open_notification()

        if contents_notification_btn.exists(2):
            print(f"  [Check] 確認通知欄是否有顯示 Notification 字樣 ")
            is_notification_pass = True
            self.d.sleep(1)
        else:
            print("  [Fail] 通知欄未顯示 Notification 字樣，測試失敗")
            self.open_ctsv_from_recents()
            self.d(text="Fail").click()

        self.open_ctsv_from_recents()

        if is_pass and is_notification_pass:
            self.d(text="Pass").click()
            print(f"  [Pass] {action} 測試成功")
        else:
            self.d(text="Fail").click()
            print(f"  [Fail] {action} 測試異常，判定失敗")


    def vpn_test(self):
        self.test_name = "VPN test"

        try:
            if not self.byod_enter_subtest(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                self.scroll_and_click(self.class_name)
                return False

            self.d.sleep(1)
            self.click_final_pass()

        except Exception as e:

            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()


    def turn_off_work_profile(self):
        self.test_name = "Turn off work profile"

        try:
            if not self.byod_enter_subtest(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                self.scroll_and_click(self.class_name)
                return False

            sub_test_map = {
                "Prepare a work notification": "_prepare_a_work_notification",
                "Please turn off work profile": "_please_turn_off_work_profile",
                "Notifications when work profile is off": "_notifications_when_work_profile_is_off",
                # "Starting work apps when work profile is off": "_starting_work_apps_when_work_profile_is_off",
                # "Please turn work profile back on": "_please_turn_work_profile_back_on",
                # "Status bar icon when work profile is on": "_status_bar_icon_when_work_profile_is_on",
                # "Starting work apps when work profile is on" : "_starting_work_apps_when_work_profile_is_on"
            }

            for action, method_name in sub_test_map.items():
                print(f"\n  [Action] 執行子測項: {action}")

                if self.d(text=action).exists(3):
                    self.d(text=action).click()
                    if self.d(text="Go").exists(2):
                        self.d(text="Go").click()

                    else:
                        self.d.sleep(1)

                    # 正常執行對應的子測項 Function
                    func = getattr(self, method_name, lambda x: print(f"  [Fail]找不到{method_name}"))
                    func(action)

                else:
                    print(f"  [Fail] 找不到 {action} 子測項")

            retry_back = 0
            while not self.d(resourceId="com.android.cts.verifier:id/pass_button").exists()  and retry_back < 5:
                self.d.press("back")
                self.d.sleep(1)
                retry_back += 1

            self.click_final_pass()

        except Exception as e:

            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    def _prepare_a_work_notification(self, action):

        print(f"    -> [Logic] 正在執行 {action} 驗證...")

        self.d.sleep(2)
        self.d.open_notification()

        contents_notification_btn = self.d(resourceId="android:id/title", text="This is a notification")

        is_notification_pass = False

        if contents_notification_btn.exists(2):
            print(f"  [Check] 確認通知欄是否有顯示 Notification 字樣 ")
            is_notification_pass = True
            self.d.sleep(1)
        else:
            print("  [Fail] 通知欄未顯示 Notification 字樣，測試失敗")
            self.open_ctsv_from_recents()
            self.d(text="Fail").click()

        self.open_ctsv_from_recents()

        if is_notification_pass:
            self.d(text="Pass").click()
            print(f"  [Pass] {action} 測試成功")
        else:
            self.d(text="Fail").click()
            print(f"  [Fail] {action} 測試異常，判定失敗")

    def _please_turn_off_work_profile(self, action):

        print(f"    -> [Logic] 正在執行 {action} 驗證...")

        self.d.sleep(1)
        self.d(resourceId="com.android.cts.verifier:id/prepare_test_button").click()

        self.d.sleep(1)
        self.settings_in_nav("Work","Work profile settings","Work apps")

        work_apps = self.d(text="Work apps")
        work_apps_switch = work_apps.right(className="android.widget.Switch")

        self.d.sleep(1)

        if work_apps_switch.info.get('checked'):
                work_apps_switch.click()

        retry_back = 0
        while not self.d(resourceId="com.android.cts.verifier:id/pass_button").exists() and retry_back < 5:
            self.d.press("back")
            self.d.sleep(1)
            retry_back += 1

        self.d.sleep(1)

    def _notifications_when_work_profile_is_off(self, action):

        print(f"    -> [Logic] 正在執行 {action} 驗證...")

        self.d.sleep(1)
        self.d.open_notification()

        contents_notification_btn = self.d(resourceId="android:id/title", text="This is a notification")

        is_notification_pass = False

        if not contents_notification_btn.exists(2):
            print(f"  [Check] 確認通知欄是否已移除 Notification 提示詞 ")
            is_notification_pass = True
            self.d.sleep(1)
        else:
            print("  [Fail] 通知欄未移除 Notification 提示詞，測試失敗")
            self.open_ctsv_from_recents()
            self.d(text="Fail").click()

        self.open_ctsv_from_recents()

        if is_notification_pass:
            self.d(text="Pass").click()
            print(f"  [Pass] {action} 測試成功")
        else:
            self.d(text="Fail").click()
            print(f"  [Fail] {action} 測試異常，判定失敗")




if __name__ == "__main__":
    task = ManagedProvisioning()
    task.byod_managed_provisioning()

    # if task.d.alive:
    #     task.d.stop_uiautomator()



    # def keyguard_disable_features(self):
    #     self.test_name = "Keyguard disable features"
    #
    #     try:
    #         if not self.byod_enter_subtest(self.test_name):
    #             print(f"  [Fail] 未能進入{self.test_name}測項")
    #             self.go_back_to_list()
    #             self.scroll_and_click(self.class_name)
    #             return False
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
