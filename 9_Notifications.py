from auto import CtsVerifier
import argparse
import json
import time
import subprocess
import uiautomator2 as u2

class Notification(CtsVerifier):
    test_mapping = {
        "Bubble Notification Tests": "bubble_notification_tests",
        "CA Cert Notification Test " : "ca_cert_notification_test",
        "CA Cert Notification on Boot test" : "ca_cert_notification_on_boot_test",
        "Condition Provider test" : "condition_provider_test",
        "Notification Dismiss Test" : "notification_dismiss_test",
        "Notification Full Screen Intent Test" : "notification_full_screen_intent_test"
    }


    def bubble_notification_tests(self):

        self.test_name = "Bubble Notification Tests"

        try :
            if not self.scroll_and_click(self.test_name): return False

            self.d.sleep(1)
            self.settings_nav("Notifications", "Bubbles")

            switch = self.d(text="Allow apps to show bubbles").right(className="android.widget.Switch")

            if not switch.info.get("checked"):
                switch.click()
                print("  [Check] 開啟 Allow apps to show bubbles")

            self.d.sleep(1)

            self.settings_nav("Apps", "CTS Verifier", "Notifications")


            if self.d(textContains="BubbleBot0").exists(2):
                print("  [Fail] 畫面不該預設有 BubbleBot0，測試失敗")
                self.open_ctsv_from_recents()
                self.click_fail()
                return False
            else:
                print("  [Check] 確認畫面未出現 BubbleBot0")

            self.d.sleep(1)
            self.open_ctsv_from_recents()


            self.d(resourceId="com.android.cts.verifier:id/test_step_passed").click(); self.d.sleep(1)
            self.d(resourceId="com.android.cts.verifier:id/bubble_test_button").click(); self.d.sleep(1)
            self.d.open_notification(); self.d.sleep(1)

            # if not self.d(resourceId="android:id/bubble_button").wait(2):
            #     bubble_button.click(); self.d.sleep(1)
            #     self.d(resourceId="android:id/bubble_button").click()
            #
            # if self.d(resourceId="android:id/bubble_button",description="Show bubble").wait(2):
            #     self.d(resourceId="android:id/bubble_button").click()
            # else:
            #     self.d(resourceId="android:id/bubble_button").click(); self.d.sleep(0.5)
            #     self.d(resourceId="android:id/bubble_button").click()


            ##############################################################################
            bubble_btn = self.d(resourceId="android:id/bubble_button")
            expand_arrow = self.d(text="BubbleBot0").right(resourceId="android:id/expand_button_pill")

            # 2. 檢查 Bubble 按鈕是否已經在畫面上
            if not bubble_btn.exists(2):
                print("  [Action] Bubble 按鈕被隱藏，點擊向下箭頭展開...")

                # 點擊展開箭頭前，也做一層防呆
                if expand_arrow.exists(timeout=2):
                    expand_arrow.click()
                    self.d.sleep(1)  # 等待展開動畫完成
                else:
                    print("  [Fail] 畫面上找不到向下展開箭頭。")

            # 3. 再次確認 Bubble 按鈕是否出現，若出現才點擊
            if bubble_btn.exists(timeout=2):
                print("  [Action] 成功找到 Bubble 按鈕，執行點擊。")
                bubble_btn.click()
                self.d.sleep(1)
            else:
                print("  [Fail] 展開後依然找不到 Bubble 按鈕，請檢查 UI 狀態。")
            ###################################################################################

            bubble = self.d(resourceId="com.android.systemui:id/bubble_view")
            if bubble.wait(2) and self.d(resourceId="com.android.cts.verifier:id/title_text").exists:
                print("  [Check] 確認畫面成功跳出 Bubble")
                bubble.click(); self.d.sleep(1)
                self.d(resourceId="com.android.cts.verifier:id/test_step_passed").click(); self.d.sleep(1)
            else:
                print("  [Fail] 畫面未成功跳出 Bubble 訊息框，測試失敗")
                self.open_ctsv_from_recents()
                self.click_fail()
                return False

            bubble.click(); self.d.sleep(1)
            if self.d(resourceId="com.android.systemui:id/stack_education_layout").exists(2):
                bubble.click()
                self.d.sleep(1)
            self.d(resourceId="com.android.systemui:id/manage_button").click(); self.d.sleep(1)
            self.d(resourceId="com.android.systemui:id/bubble_manage_menu_settings_name").click(); self.d.sleep(1)

            bubble_option = self.d(resourceId="com.android.settings:id/bubble_selected")
            bubble_option_info = bubble_option.info

            if bubble_option_info.get("selected") or bubble_option_info.get("checked"):
                self.open_ctsv_from_recents()
                self.d(resourceId="com.android.cts.verifier:id/test_step_passed").click()
                print("  [Check] Bubble Option Info 已被 Selected")
                self.d.sleep(1)
            else:
                print("  [Fail] App未自動變更成 Selected conversations can bubble，測試失敗")
                self.open_ctsv_from_recents()
                self.click_fail()
                return False

            self.d(resourceId="com.android.cts.verifier:id/bubble_test_button").click(); self.d.sleep(1)
            self.settings_in_nav("Bubbles", "Allow apps to show bubbles")







            """"""
            switch = self.d(text="Allow apps to show bubbles").right(className="android.widget.Switch")
            """"""









            if switch.info.get("checked"):
                switch.click()
                print("  [Check] 關閉 Allow apps to show bubbles")

            self.open_ctsv_from_recents()

            if self.d(className="android.widget.TextView",textContains="State is correct").exists(2):
                self.d(resourceId="com.android.cts.verifier:id/test_step_passed").click()
                self.d.sleep(1)
            else:
                print("  [Fail] State isn't correct，測試失敗")
                self.open_ctsv_from_recents()
                self.click_fail()
                return False

            self.d(resourceId="com.android.cts.verifier:id/bubble_test_button").click(); self.d.sleep(1)
            self.d(resourceId="com.android.settings:id/bubble_all").click(); self.d.sleep(1)

            if self.d(className="android.widget.TextView",text="Turn on bubbles for device?").exists(2):
                self.d(text="Turn on").click()
                print("  [Check] All conversation can Bubble 設定成功")
                self.d.sleep(1)
            else:
                print("  [Fail] All conversation can Bubble 設定異常，測試失敗")
                self.open_ctsv_from_recents()
                self.click_fail()
                return False

            self.open_ctsv_from_recents()

            if self.d(className="android.widget.TextView",textContains="State is correct").exists(2):
                self.d(resourceId="com.android.cts.verifier:id/test_step_passed").click()
                self.d.sleep(1)
            else:
                print("  [Fail] State isn't correct，測試失敗.")
                self.open_ctsv_from_recents()
                self.click_fail()
                return False

            self.d(resourceId="com.android.cts.verifier:id/bubble_test_button").click(); self.d.sleep(1)

            is_pass = False

            if bubble.wait(2):
                self.d.open_notification()
                if self.d(resourceId="android:id/conversation_icon").wait(2) and self.d(text="Send bubble notification").exists:
                    is_pass = True

            self.d.press("back")
            self.d.sleep(2)

            if is_pass:
                self.d(resourceId="com.android.cts.verifier:id/test_step_passed").click()
                self.d.sleep(2)
            else:
                print("  [Fail] Bubble 未正常跳出，測試失敗.")
                self.open_ctsv_from_recents()
                self.click_fail()
                return False

            self.d(resourceId="com.android.cts.verifier:id/bubble_test_button").click()
            self.d.sleep(1)

            is_pass2 = False

            if bubble.wait(2):
                self.d.open_notification()
                if not self.d(resourceId="android:id/conversation_icon").exists(2) and not self.d(text="BubbleBot0").exists(2):
                    is_pass2 = True

            self.d.press("back")
            self.d.sleep(2)

            if is_pass2:
                self.d(resourceId="com.android.cts.verifier:id/test_step_passed").click()
                print("  [Check] 驗證 Bubble 正常隱藏")
                self.d.sleep(2)
            else:
                print("  [Fail] Bubble 未正常隱藏，測試失敗.")
                self.open_ctsv_from_recents()
                self.click_fail()
                return False

            self.d(resourceId="com.android.cts.verifier:id/bubble_test_button").click()
            self.d.sleep(1)

            is_pass3 = False

            if bubble.wait(2):
                self.d.open_notification()
                if self.d(resourceId="android:id/conversation_icon").wait(2) and self.d(text="BubbleBot0").exists:
                    is_pass3 = True

            self.d.press("back")
            self.d.sleep(2)

            if is_pass3:
                self.d(resourceId="com.android.cts.verifier:id/test_step_passed").click()
                print("  [Check] 驗證 Bubble 有跳出，通知欄無訊息")
                self.d.sleep(2)
            else:
                print("  [Fail] Bubble 設定異常，測試失敗")
                self.open_ctsv_from_recents()
                self.click_fail()
                return False

            self.d(resourceId="com.android.cts.verifier:id/bubble_test_button",text="Remove bubble").click()
            self.d.sleep(1)

            is_pass4 = False

            if not bubble.wait(2):
                self.d.open_notification()
                if self.d(resourceId="android:id/conversation_icon").wait(2) and self.d(text="BubbleBot0").exists:
                    is_pass4 = True

            self.d.press("back")
            self.d.sleep(2)

            if is_pass4:
                self.d(resourceId="com.android.cts.verifier:id/test_step_passed").click()
                print("  [Check] 驗證 Bubble 清除訊息功能正常")
                self.d.sleep(2)
            else:
                print("  [Fail] Bubble 清除異常，測試失敗")
                self.open_ctsv_from_recents()
                self.click_fail()
                return False

            self.d(resourceId="com.android.cts.verifier:id/bubble_test_button", text="Add bubble").click()
            self.d.sleep(1)

            is_pass5 = False

            if  bubble.wait(3):
                self.d.open_notification()
                if self.d(resourceId="android:id/conversation_icon").wait(2) and self.d(text="Add bubble").exists:
                    is_pass5 = True

            self.d.press("back")
            self.d.sleep(2)

            if is_pass5:
                self.d(resourceId="com.android.cts.verifier:id/test_step_passed").click()
                print("  [Check] 驗證 Bubble 添加成功")
                self.d.sleep(2)
            else:
                print("  [Fail] Bubble 添加異常，測試失敗")
                self.open_ctsv_from_recents()
                self.click_fail()
                return False

            is_pass6 = False

            if bubble.wait(2):
                bubble.click(); self.d.sleep(0.5)
                bubble.click()
                self.d.open_notification()
                if not self.d(resourceId="android:id/conversation_icon").exists(2) and not self.d(text="BubbleBot0").exists(2):
                    is_pass6 = True

            self.d.press("back")
            self.d.sleep(2)

            if is_pass6:
                self.d(resourceId="com.android.cts.verifier:id/test_step_passed").click()
                print("  [Check] 驗證雙擊 Bubble，通知欄訊息會消失")
                self.d.sleep(2)
            else:
                print("  [Fail] 雙擊 Bubble 設定異常，測試失敗")
                self.open_ctsv_from_recents()
                self.click_fail()
                return False

            self.d(resourceId="com.android.cts.verifier:id/bubble_test_button", text="Update bubble to show notification").click()
            self.d.sleep(1)

            is_pass7 = False
            is_disappeared = False

            if bubble.wait(3):
                self.d.open_notification()
                if self.d(resourceId="android:id/conversation_icon").wait(2) and self.d(text="BubbleBot0").exists:
                    is_pass7 = True

            self.d.press("back")
            self.d.sleep(2)

            w, h = self.d.window_size()
            end_x = w * 0.5
            end_y = h * 0.95
            if bubble.exists:
                start_x, start_y = bubble.center()
                self.d.drag(start_x, start_y, end_x, end_y, duration=1.0)

                print("  [Check] Bubble 拖曳動作完成")
            else:
                print("  [Fail] 找不到 Bubble，無法執行拖曳")

            self.d.sleep(2)

            if not bubble.wait(3):
                self.d.open_notification()
                if self.d(resourceId="android:id/conversation_icon").wait(2) and self.d(text="BubbleBot0").exists:
                    is_disappeared = True

            self.d.press("back")
            self.d.sleep(2)


            if is_pass7 and is_disappeared:
                self.d(resourceId="com.android.cts.verifier:id/test_step_passed").click()
                print("  [Check] 驗證 UPDATE BUBBLE TO SHOW NOTIFICATION 功能正常")
                self.d.sleep(2)
            else:
                print("  [Fail] UPDATE BUBBLE TO SHOW NOTIFICATION 功能異常，測試失敗")
                self.open_ctsv_from_recents()
                self.click_fail()
                return False

            self.d(resourceId="com.android.cts.verifier:id/bubble_test_button",text="Send bubble notification").click()
            self.d.sleep(1)

            is_pass8 = False
            is_bubble_disappeared = False
            is_notification_disappeared = False

            if bubble.wait(3):
                self.d.open_notification()
                if self.d(resourceId="android:id/conversation_icon").wait(2) and self.d(text="BubbleBot0").exists:
                    is_pass8 = True


            self.clear_all_notifications()
            self.d.sleep(5)

            if not self.d(description="CTS Verifier notification: ").wait(3):
                print("  [Check] 刪除 Bubble 通知 ")
                is_bubble_disappeared = True
            else:
                print("  [Fail] 未能刪除 Bubble 通知，測試失敗")

            self.d.sleep(2)

            if bubble.wait(3):
                is_notification_disappeared = True

            if is_pass8 and is_bubble_disappeared and is_notification_disappeared:
                self.d(resourceId="com.android.cts.verifier:id/test_step_passed").click()
                print("  [Check] 驗證 SEND BUBBLE NOTIFICATION 功能正常")
                self.d.sleep(2)
            else:
                print("  [Fail] SEND BUBBLE NOTIFICATION 功能異常，測試失敗")
                print(f" is_pass8 = {is_pass8}, is_bubble_disappeared = {is_bubble_disappeared}, is_notification_disappeared = {is_notification_disappeared}")
                self.click_fail()
                return False

            #########################################################################################

            self.d(resourceId="com.android.cts.verifier:id/bubble_test_button").click()
            self.d.sleep(1)

            is_pass9 = False

            if self.d(resourceId="com.android.cts.verifier:id/title_text").wait(3) and self.d(resourceId="com.android.cts.verifier:id/edit_text").exists:
                    is_pass9 = True

            self.d.press("back")
            self.d.sleep(2)

            if is_pass9 :
                self.d(resourceId="com.android.cts.verifier:id/test_step_passed").click()
                print("  [Check] 驗證 Bubble Text 開啟功能正常")
                self.d.sleep(2)
            else:
                print("  [Fail] Bubble Text 功能異常，測試失敗")
                self.click_fail()
                return False

            #########################################################################################

            self.d.sleep(1)

            is_pass10 = False
            text_connect = "Bubble expanded view"

            if bubble.wait(3):
                bubble.click()
                self.d.sleep(2)
                if self.d(resourceId="com.android.cts.verifier:id/title_text").info.get("text") == text_connect:
                    is_pass10 = True

            self.d.press("back")
            self.d.sleep(2)

            if is_pass10:
                self.d(resourceId="com.android.cts.verifier:id/test_step_passed").click()
                print("  [Check] 驗證 Bubble Text Empty")
                self.d.sleep(2)
            else:
                print("  [Fail] Bubble Text not Empty，測試失敗")
                self.click_fail()
                return False

            ########################################################################################
            self.d(resourceId="com.android.cts.verifier:id/bubble_test_button").click()
            self.d.sleep(2)

            bubble0 = self.d(descriptionContains="BubbleBot0")
            bubble1 = self.d(descriptionContains="BubbleBot1")
            bubble2 = self.d(descriptionContains="BubbleBot2")

            if not bubble.wait(3):
                print("  [Fail] 畫面上找不到主要的 bubble_view 可以點擊")
                self.click_fail()
                return False

            bubble.click()
            self.d.sleep(1)

            found_three_bubbles = False
            for _ in range(3):
                if bubble0.exists() and bubble1.exists() and bubble2.exists():
                    found_three_bubbles = True
                    break
                self.d.sleep(1)

            if not found_three_bubbles:
                print("  [Fail] 未出現三個 Bubble Chat,測試失敗")
                self.d.press("back")
                self.click_fail()
                return False

            print("  [Check] 成功展開並找到三個 Bubble Chat")


            w, h = self.d.window_size()
            end_x = w * 0.5
            end_y = h * 0.95
            start_x2, start_y2 = bubble2.center()

            self.d.drag(start_x2, start_y2, end_x, end_y, duration=1.0)

            if bubble2.exists(2):
                print("  [Fail] Bubble 未能刪除，測試失敗")
                self.d.press("back")
                self.click_fail()
                return False

            print("  [Check] Bubble 刪除動作完成")

            self.d.sleep(1)
            self.d(resourceId="com.android.systemui:id/bubble_overflow_button").click()
            self.d.sleep(1)

            if not bubble2.exists(2):
                print("  [Fail] Bubble 未能移至頁面，測試失敗")
                self.d.press("back")
                self.click_fail()
                return False

            print("  [Check] Bubble 移至頁面完成")

            bubble0.click()
            self.d.sleep(1)
            self.d.press("back")
            self.d.sleep(1)

            # 👉 如果程式能順利走到這裡，代表前面所有的 return False 都沒有被觸發
            # 直接點擊 Pass，不需要任何 if 判斷！
            self.d(resourceId="com.android.cts.verifier:id/test_step_passed").click()
            print("  [Check] 驗證 Send several bubbles 成功")
            self.d.sleep(2)
            #######################################################################################
            is_pass12 = False
            bubble0 = self.d(descriptionContains="BubbleBot0")
            bubble1 = self.d(descriptionContains="BubbleBot1")
            bubble2 = self.d(descriptionContains="BubbleBot2")

            if bubble.wait(3):
                bubble.click()
                self.d.sleep(1)
                self.d(resourceId="com.android.systemui:id/bubble_overflow_button").click()
                if  bubble2.exists(3):
                    is_pass12 = True
                else:
                    print("  [Fail] 頁面未出現刪除的 Bubble Chat,測試失敗")
                    bubble0.click()
                    self.d.sleep(1)
                    self.d.press("back")
                    self.d.sleep(1)
                    self.click_fail()

            bubble2.click()
            self.d.sleep(1)

            bubble_back = False
            if bubble0.wait(2) and bubble1.exists and  bubble2.exists:
                bubble_back = True
                print("  [Check] Bubble 復原完成")
            else:
                print("  [Fail] Bubble 未能復原，測試失敗")
                bubble0.click()
                self.d.sleep(1)
                self.d.press("back")
                self.d.sleep(1)
                self.click_fail()

            self.d.sleep(1)
            self.d.press("back")

            self.d.sleep(1)

            if is_pass12 and bubble_back:
                self.d(resourceId="com.android.cts.verifier:id/test_step_passed").click()
                print("  [Check] 驗證復原動作成功")
                print("  [Check] Add bubble from overflow 驗證正常")
                self.d.sleep(2)
            else:
                print("  [Fail] 復原動作異常，測試失敗")
                self.click_fail()
                return False

            ########################################################################################
            self.d.sleep(1)

            bubble0 = self.d(descriptionContains="BubbleBot0")
            bubble1 = self.d(descriptionContains="BubbleBot1")
            bubble2 = self.d(descriptionContains="BubbleBot2")

            self.d(resourceId="com.android.cts.verifier:id/bubble_test_button").click()
            is_pass13 = False


            if bubble.wait(3):
                bubble.click()
                self.d.sleep(1)
                self.d(resourceId="com.android.systemui:id/bubble_overflow_button").click()
                if not bubble1.wait(3) and not bubble2.exists:
                    is_pass13 = True
                    print("  [Check] Bubble 清除並重新發布")
                else:
                    print("  [Fail] 頁面未清除前一測試的 Bubble Chat,測試失敗")

            bubble0.click()
            self.d.sleep(1)
            self.d.press("back")
            self.d.sleep(1)


            if is_pass13:
                self.d(resourceId="com.android.cts.verifier:id/test_step_passed").click()
                print("  [Check] 驗證 Bubble 重新發布功能正常")
            else:
                self.click_fail()
                return False

            ########################################################################################
            self.d.sleep(1)

            self.d(resourceId="com.android.cts.verifier:id/bubble_test_button").click()
            bubble_icon = self.d(resourceId="com.android.systemui:id/bubble_view")

            self.d.sleep(1)

            w, h = self.d.window_size()
            end_x = w * 0.5
            end_y = h * 0.95
            start_x0, start_y0 = bubble_icon.center()

            self.d.drag(start_x0, start_y0, end_x, end_y, duration=1.0)

            self.d.sleep(1)
            self.d.open_notification()

            self.d.sleep(1)
            self.d(text="BubbleBot0").click()

            bubble0 = self.d(descriptionContains="BubbleBot0")

            is_pass14 = False
            if bubble0.wait(3):
                is_pass14 = True
                print("  [Check] Bubble 從螢幕移除並從通知欄開啟")
            else:
                print("  [Fail] Bubble 無法從螢幕移除並從通知欄開啟,測試失敗")

            bubble0.click()
            self.d.sleep(1)

            if is_pass14:
                self.d(resourceId="com.android.cts.verifier:id/test_step_passed").click()
                print("  [Check] 驗證 Bubble 從螢幕移除並從通知欄開啟功能正常")
            else:
                self.click_fail()
                return False

            ########################################################################################
            self.d.sleep(1)

            bubble.click()

            is_pass15 = True
            print("  [Action] 切換為直向模式...")
            self.d.set_orientation("n")
            self.d.sleep(2.5)  # 等待畫面旋轉與重新渲染
            if not self.verify_bubble_position("portrait"):
                is_pass15 = False

            print("  [Action] 切換為橫向模式...")
            self.d.set_orientation("l")
            self.d.sleep(2.5)
            if not self.verify_bubble_position("landscape"):
                is_pass15 = False

            self.d.sleep(1.5)
            print("  [Action] 返回為直向模式...")
            self.d.set_orientation("n")
            self.d.sleep(1)
            self.d(resourceId="com.android.systemui:id/bubble_view").click()
            self.d.sleep(1)

            if is_pass15:
                self.d(resourceId="com.android.cts.verifier:id/test_step_passed").click()
                print("  [Check] 驗證螢幕轉向提示詞顯示正常")
            else:
                self.click_fail()
                return False

            ########################################################################################
            self.d.sleep(2)

            self.d(resourceId="com.android.cts.verifier:id/test_step_passed").click()

            ########################################################################################
            self.d.sleep(1)

            bubble.click()
            bubble0 = self.d(description="Bubble Chat: BubbleBot0 from CTS Verifier")
            ime = self.d(resourceId="com.android.cts.verifier:id/edit_text")
            input_field = self.d(resourceId="com.android.cts.verifier:id/edit_text")
            ime.click()

            is_pass16 = False
            if input_field.wait(3):
                input_field.set_text("test pass")
                self.d.sleep(1)

                self.d.press("enter")
                self.d.sleep(1)

                if self.d(text="test pass").exists:
                    is_pass16 = True
                    print("  [Pass] 驗證成功：IME 上方已正確顯示 'test pass'")
                else:
                    print("  [Fail] 驗證失敗：畫面上未偵測到 'test pass' 字樣。")
            else:
                print("  [Fail] 找不到輸入框，無法執行文字輸入。")

            self.d.sleep(1)
            bubble0.click()
            self.d.sleep(1)

            if is_pass16:
                self.d(resourceId="com.android.cts.verifier:id/test_step_passed").click()
                print("  [Check] 驗證打字框 IME 功能正常")
            else:
                self.click_fail()
                return False

            ########################################################################################
            self.d.sleep(1)

            bubble0 = self.d(description="Bubble Chat: BubbleBot0 from CTS Verifier")
            ime = self.d(resourceId="com.android.cts.verifier:id/test_message")

            self.d(resourceId="com.android.cts.verifier:id/bubble_test_button").click()
            self.d.sleep(1)
            bubble.click()

            is_pass17 = False
            if ime.info.get("text") == "Test Passed!":
                is_pass17 = True

            self.d.sleep(1)
            bubble0.click()
            self.d.sleep(1)

            if is_pass17:
                self.d(resourceId="com.android.cts.verifier:id/test_step_passed").click()
                print("  [Check] 驗證 SMALL HEIGHT BUBBLE 打字框顯示字樣功能正常")
            else:
                self.click_fail()
                return False

            ########################################################################################
            self.d.sleep(1)

            bubble0 = self.d(description="Bubble Chat: BubbleBot0 from CTS Verifier")
            ime = self.d(resourceId="com.android.cts.verifier:id/test_message")

            self.d(resourceId="com.android.cts.verifier:id/bubble_test_button").click()
            self.d.sleep(1)
            bubble.click()

            is_pass18 = False
            if ime.info.get("text") == "Test Passed!":
                is_pass18 = True

            self.d.sleep(1)
            bubble0.click()
            self.d.sleep(1)

            if is_pass18:
                self.d(resourceId="com.android.cts.verifier:id/test_step_passed").click()
                print("  [Check] 驗證 MAX HEIGHT BUBBLE 打字框顯示字樣功能正常")
            else:
                self.click_fail()
                return False

            if self.d(resourceId="com.android.cts.verifier:id/pass_button", enabled=True).wait(5):
                self.click_pass()
            else:
                print(f"  [Fail] {self.test_name} 測試失敗")
                self.click_fail()

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    def verify_bubble_position(self, orientation_mode):
        """
        驗證 Bubble 展開視窗的位置
        :param orientation_mode: "portrait" (直向) 或 "landscape" (橫向)
        """
        # 1. 定義要抓取的目標 UI (以截圖中的 title_text 為基準)
        title_view = self.d(resourceId="com.android.cts.verifier:id/title_text")
        if not title_view.wait(timeout=3):
            print(f"  [Fail] {orientation_mode} 模式下，未偵測到 Bubble 標題文字")
            return False

        # 核心優化 1：透過 XPath 往上抓取父容器 (Parent Container)
        # 這樣拿到的 bounds 才會是整個 Bubble 視窗的實際大小，而非單行文字的大小
        bubble_container = self.d.xpath('//*[@resource-id="com.android.cts.verifier:id/title_text"]/..')

        # 取得當下螢幕的寬度與高度
        screen_width, screen_height = self.d.window_size()

        # 取得父容器的四個頂點座標
        bounds = bubble_container.info['bounds']
        top_y = bounds['top']
        left_x = bounds['left']
        right_x = bounds['right']

        # 算出視窗整體的 X 軸中心點
        center_x = (left_x + right_x) / 2

        # 依照方向進行嚴格邏輯判定
        if orientation_mode == "portrait":
            # 核心優化 2：直向嚴格判斷前 30%
            if top_y < (screen_height * 0.3):
                print("  [Pass] 直向驗證成功")
                return True
            else:
                print(f"  [Fail] 直向驗證失敗：Bubble 未達頂部標準 (Top: {top_y} >= {screen_height * 0.3})")
                return False


        elif orientation_mode == "landscape":

            # 計算中心點佔螢幕寬度的比例 (0.0 ~ 1.0)
            ratio = center_x / screen_width
            # 核心優化 3：支援左側、右側，以及大螢幕/PCB板常見的「置中」
            if ratio < 0.35:
                print("  [Pass] 橫向驗證成功：Bubble 在螢幕【左側】")
                return True
            elif ratio > 0.65:
                print("  [Pass] 橫向驗證成功：Bubble 在螢幕【右側】")
                return True
            elif 0.40 <= ratio <= 0.60:
                print("  [Pass] 橫向驗證成功：Bubble 在螢幕【置中】")
                return True
            else:
                print(f"  [Fail] 橫向驗證失敗：Bubble 位置無法判定 (CenterX: {center_x})")
                return False


    def ca_cert_notification_test(self):
        self.test_name = "CA Cert Notification Test"

        try:
            if not self.scroll_and_click(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                return False

            self.d(textContains="Tap to install a CA certificate").click()

            if self.d(resourceId="android:id/scrollView").exists(3):
                self.d(text="Go").click()
                self.d.sleep(1)
                self.settings_in_nav("More security & privacy", "Encryption & credentials", "Install a certificate", "CA certificate","Install anyway")

            is_install = False
            if self.d(text="myCA.cer").exists(5):
                is_install = True
                self.d(text="myCA.cer").click()

            self.d.sleep(2)

            retry_back = 0
            while not self.d(text="Pass").exists() and not self.d(text="Fail").exists() and retry_back < 6:
                self.d.press("back")
                self.d.sleep(1)
                retry_back += 1

            if is_install:
                self.d(text="Pass").click()
            else:
                self.d(text="Fail").click()
                self.d.sleep(1)
                self.click_fail()
                return False

            self.d.sleep(1)
            test_text_1 = "Visit the user-installed trusted credentials page and confirm that the Internet Widgits Pty Ltd cert appears in the list."

            self.d(text=test_text_1).click()

            if self.d(resourceId="android:id/contentPanel").exists(3):
                self.d(text="Go").click()
                self.d.sleep(1)

            is_test_text_1_pass = False
            trusted_credential = self.d(resourceId="com.android.settings:id/trusted_credential_subject_primary")
            if trusted_credential.info.get("text") == "Internet Widgits Pty Ltd":
                is_test_text_1_pass = True

            retry_back = 0
            while not self.d(text="Pass").exists() and not self.d(text="Fail").exists() and retry_back < 2:
                self.d.press("back")
                self.d.sleep(1)
                retry_back += 1

            if is_test_text_1_pass:
                self.d(text="Pass").click()
            else:
                self.d(text="Fail").click()
                self.d.sleep(1)
                self.click_fail()
                return False

            self.d.sleep(1)
            test_text_2 = "You may have been prompted to set a screen lock when installing the certificate. If so, remove it. If not, you may skip this step."

            self.d(text=test_text_2).click()

            if self.d(resourceId="android:id/contentPanel").exists(3):
                self.d(text="Go").click()
                self.d.sleep(1)

            if self.d(text="Continue without fingerprint").exists(2):
                self.d(text="Continue without fingerprint").click()

            self.d.sleep(1)
            self.d(text="None").click()

            self.d.sleep(2)

            self.d(text="Pass").click()

            test_text_3 = "Look at the system notifications"
            self.d(textContains=test_text_3).click()
            print("  [Check] 系統會自動判定...")
            self.d.sleep(2)

            self.d.open_notification()
            self.d(text="Certificate authority installed").click()
            self.d.sleep(1)
            self.d(text="Check certificate").click()
            self.d.sleep(1)
            self.d(text="Uninstall").click()
            self.d.sleep(3)

            is_pass = True
            if trusted_credential.exists(2):
                is_pass = False

            self.d.press("back")

            if not is_pass:
                print("  [Fail] trusted_credential 未能成功解除安裝, 測試失敗")
                self.click_fail()
                return False

            self.d.sleep(2)
            test_text_4 = "Open the notification and follow the link"
            self.d(textContains=test_text_4).click()
            print("  [Check] 系統自動判定，是否成功刪除證書...")

            self.d.sleep(2)
            if self.d(resourceId="com.android.cts.verifier:id/pass_button", enabled=True).wait(5):
                self.click_pass()
            else:
                print(f"  [Fail] {self.test_name} 測試失敗")
                self.click_fail()

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    def ca_cert_notification_on_boot_test(self):
        self.test_name = "CA Cert Notification on Boot test"

        try:
            if not self.scroll_and_click(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                return False

            self.settings_nav("Security & privacy","More security & privacy", "Encryption & credentials", "Install a certificate", "CA certificate","Install anyway","myCA.cer", max_depth=8)

            self.open_ctsv_from_recents()

            self.d(resourceId="com.android.cts.verifier:id/check_creds").click()
            self.d.sleep(2)

            is_test_text_1_pass = False
            trusted_credential = self.d(resourceId="com.android.settings:id/trusted_credential_subject_primary")
            if trusted_credential.info.get("text") == "Internet Widgits Pty Ltd":
                is_test_text_1_pass = True

            self.d.press("back")

            if is_test_text_1_pass:
               self.d.sleep(1)
            else:
                self.click_fail()
                return False

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
            self.scroll_and_click(self.test_name)

            if self.d(resourceId=self.btn_pass).exists(3):
                self.click_pass()
            else:
                self.click_fail()

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    def condition_provider_test(self):

        self.test_name = "Condition Provider test"

        try:
            if not self.scroll_and_click(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                return False

            self.d(resourceId="com.android.cts.verifier:id/nls_action_button").click()
            self.d.sleep(2)

            if self.d(scrollable=True).scroll.to(text="CTS Verifier"):
                self.d.sleep(1)
                self.d(text="CTS Verifier").click()

            do_not_disturb = self.d(text="Allow Do Not Disturb")
            do_not_disturb_switch = do_not_disturb.right(className="android.widget.Switch")

            self.d.sleep(1)

            if not do_not_disturb_switch.info.get('checked'):
                do_not_disturb_switch.click()
                if self.d(resourceId="com.android.settings:id/alertTitle").exists(3):
                    self.d(text="Allow").click()

            retry_back = 0
            while not self.d(resourceId=self.btn_pass).exists() and retry_back < 3:
                self.d.press("back")
                self.d.sleep(1)
                retry_back += 1

            self.d.sleep(60)

            launch_settings = self.d(resourceId="com.android.cts.verifier:id/nls_action_button",enabled=True)
            if not launch_settings.wait(3):
                self.d(scrollable=True).scroll.to(resourceId="com.android.cts.verifier:id/nls_action_button",enabled=True)
                self.d.sleep(1)
            if launch_settings.exists(2):
                launch_settings.click()
            else:
                print("  [Fail] 滾動到底部仍找不到 Launch Settings")
                self.click_fail()
                return False

            is_123_appear = False
            if self.d(text="123").exists(3):
                is_123_appear = True

            self.d.press("back")

            if is_123_appear:
                self.click_fail()
                print("  [Fail] 不該出現 123 開關，測試失敗")
                return False
            else:
                print("  [Check] 驗證 Schedules 畫面顯示正常")
                self.d.sleep(2)
                pass_btn = self.d(resourceId="com.android.cts.verifier:id/iva_action_button_pass", enabled=True)
                if not pass_btn.wait(3):
                    self.d(scrollable=True).scroll.to(resourceId="com.android.cts.verifier:id/iva_action_button_pass", enabled=True)
                    self.d.sleep(1)
                    pass_btn.click()
                else:
                    print("  [Fail] 滾動到底部仍找不到 Pass 按鈕")
                    self.click_fail()
                    return False

            launch_settings = self.d(resourceId="com.android.cts.verifier:id/nls_action_button", enabled=True)
            if not launch_settings.wait(3):
                self.d(scrollable=True).scroll.to(resourceId="com.android.cts.verifier:id/nls_action_button", enabled=True)
                self.d.sleep(1)
            if launch_settings.exists(2):
                launch_settings.click()
            else:
                print("  [Fail] 滾動到底部仍找不到 Launch Settings 2")
                self.click_fail()
                return False


            self.d.sleep(1)
            btn_123 = self.d(text="123")
            btn_123_switch = btn_123.right(className="android.widget.Switch")

            self.d.sleep(1)

            if btn_123_switch.info.get('checked'):
                btn_123_switch.click()
                print("  [Check] 關閉 123 button")

            self.d.press("back")
            self.d.sleep(5)

            launch_settings = self.d(resourceId="com.android.cts.verifier:id/nls_action_button", enabled=True)
            if not launch_settings.wait(3):
                self.d(scrollable=True).scroll.to(resourceId="com.android.cts.verifier:id/nls_action_button",enabled=True)
                self.d.sleep(1)
            if launch_settings.exists(2):
                launch_settings.click()
            else:
                print("  [Fail] 滾動到底部仍找不到 Launch Settings 3")
                self.click_fail()
                return False

            self.d.sleep(1)
            btn_123 = self.d(text="123")
            btn_123_switch = btn_123.right(className="android.widget.Switch")

            self.d.sleep(1)

            if not btn_123_switch.info.get('checked'):
                btn_123_switch.click()

            self.d.press("back")
            self.d.sleep(5)

            launch_settings = self.d(resourceId="com.android.cts.verifier:id/nls_action_button", enabled=True)
            if not launch_settings.wait(3):
                self.d(scrollable=True).scroll.to(resourceId="com.android.cts.verifier:id/nls_action_button",enabled=True)
                self.d.sleep(1)
            if launch_settings.exists(2):
                launch_settings.click()
            else:
                print("  [Fail] 滾動到底部仍找不到 Launch Settings 4")
                self.click_fail()
                return False

            self.d.sleep(1)
            delete_btn = self.d(description="More options")
            delete_btn.click()
            self.d.sleep(1)
            self.d(className="android.widget.TextView", text="Delete schedules").click()
            self.d.sleep(1)
            self.d(text="123").click()
            self.d.sleep(1)

            if self.d(text="123").info.get('checked'):
                self.d(text="Delete").click()
                print("  [Check] 刪除 123 button")
            else:
                retry_back = 0
                while not self.d(resourceId=self.btn_pass).exists() and retry_back < 3:
                    self.d.press("back")
                    self.d.sleep(1)
                    retry_back += 1

                print("  [Fail] 無法刪除 123 開關，測試失敗")
                self.click_fail()
                return False

            self.d.press("back")
            self.d.sleep(60)

            launch_settings = self.d(resourceId="com.android.cts.verifier:id/nls_action_button", enabled=True)
            if not launch_settings.wait(3):
                self.d(scrollable=True).scroll.to(resourceId="com.android.cts.verifier:id/nls_action_button",
                                                  enabled=True)
                self.d.sleep(1)
            if launch_settings.exists(2):
                launch_settings.click()
            else:
                print("  [Fail] 滾動到底部仍找不到 Launch Settings 5")
                self.click_fail()
                return False

            if self.d(scrollable=True).scroll.to(text="CTS Verifier"):
                self.d.sleep(1)
                self.d(text="CTS Verifier").click()

            do_not_disturb = self.d(text="Allow Do Not Disturb")
            do_not_disturb_switch = do_not_disturb.right(className="android.widget.Switch")

            self.d.sleep(1)

            if do_not_disturb_switch.info.get('checked'):
                do_not_disturb_switch.click()

            self.d.sleep(3)
            retry_back = 0
            while not self.d(resourceId=self.btn_pass).exists() and retry_back < 3:
                self.d.press("back")
                self.d.sleep(1)
                retry_back += 1

            self.d.sleep(10)

            if self.d(resourceId=self.btn_pass).exists(timeout=3):
                self.click_pass()
            else:
                self.click_fail()

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    def notification_dismiss_test(self):

        self.test_name = "Notification Dismiss Test"

        self.set_screen_lock()

        try:
            if not self.scroll_and_click(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                return False

            print("  [Check] 系統自動判定中...")

            if not self.d(text="Launch Channel Settings", enabled=True).exists(15):
                self.d(scrollable=True).scroll.to(text="Launch Channel Settings", enabled=True)
                self.d.sleep(1)
            self.d(text="Launch Channel Settings", enabled=True).click()

            self.d.sleep(1)
            self.settings_in_nav("Lock screen","Show sensitive content only when unlocked")

            retry_back = 0
            while not self.d(resourceId=self.btn_pass).exists() and retry_back < 3:
                self.d.press("back")
                self.d.sleep(1)
                retry_back += 1

            self.d.sleep(2)
            self.d.open_notification()

            notification_dismiss_arrow = self.d(text="NotifDismissTest").right(resourceId="android:id/expand_button_pill")
            if notification_dismiss_arrow.exists(2):
                print("  [Check] 在通知欄有出現 NotifDismissTest")
                bounds = notification_dismiss_arrow.info['bounds']

                center_y = (bounds['top'] + bounds['bottom']) // 2
                center_x = (bounds['left'] + bounds['right']) // 2

                print(f"  [Action] 準備刪除 NotifDismissTest")

                self.d.swipe(center_x, center_y, 0, center_y, duration=0.5)
                self.d.sleep(3)
                is_massage_deleted = True
                if self.d(text="NotifDismissTest").exists(3):
                    is_massage_deleted = False
            else:
                print("  [Fail] 找不到 NotifDismissTest")
                self.open_ctsv_from_recents()
                self.click_fail()
                return False

            self.open_ctsv_from_recents()

            pass_btn = self.d(resourceId="com.android.cts.verifier:id/iva_action_button_pass", enabled=True)
            if pass_btn.wait(3) and is_massage_deleted:
                print("  [Check] NotifDismissTest 不應該被刪除")
                self.d(scrollable=True).scroll.to(resourceId="com.android.cts.verifier:id/iva_action_button_pass",enabled=True)
                self.d.sleep(1)
                pass_btn.click()
            else:
                print("  [Fail] 滾動到底部仍找不到 Pass 按鈕")
                self.click_fail()
                return False

            self.d.sleep(1)
            self.d.press("power")
            self.d.sleep(2)
            self.d.press("power")

            notification_dismiss_arrow = self.d(text="NotifDismissTest").right(resourceId="android:id/expand_button_pill")
            if notification_dismiss_arrow.exists(2):
                print("  [Check] 在桌面有顯示 NotifDismissTest")
                bounds = notification_dismiss_arrow.info['bounds']

                center_y = (bounds['top'] + bounds['bottom']) // 2
                center_x = (bounds['left'] + bounds['right']) // 2

                print(f"  [Action] 準備刪除 NotifDismissTest")

                self.d.swipe(center_x, center_y, 0, center_y, duration=0.5)
                self.d.sleep(2)
                is_massage_deleted = False
                if self.d(text="NotifDismissTest").exists(3):
                    is_massage_deleted = True

            else:
                print("  [Fail] 找不到 NotifDismissTest")
                self.unlock_device()
                self.d.sleep(1)
                self.click_fail()
                return False

            self.unlock_device()
            self.d.sleep(1)

            pass_btn = self.d(resourceId="com.android.cts.verifier:id/iva_action_button_pass", enabled=True)
            if not pass_btn.wait(1):
                self.d(scrollable=True).scroll.to(resourceId="com.android.cts.verifier:id/iva_action_button_pass",enabled=True)

            if pass_btn.exists and is_massage_deleted:
                print("  [Check] NotifDismissTest 不應該被刪除")
                self.d.sleep(1)
                pass_btn.click()
            else:
                print("  [Fail] 滾動到底部仍找不到 Pass 按鈕 1")
                self.click_fail()
                return False

            self.d.sleep(1)
            self.d.press("power")
            self.d.sleep(2)
            self.d.press("power")

            notification_dismiss_arrow = self.d(text="NotifDismissTest").right(resourceId="android:id/expand_button_pill")
            if notification_dismiss_arrow.exists(2):
                print("  [Check] 在桌面有顯示 NotifDismissTest")
                bounds = notification_dismiss_arrow.info['bounds']

                center_y = (bounds['top'] + bounds['bottom']) // 2
                center_x = (bounds['left'] + bounds['right']) // 2

                print(f"  [Action] 準備刪除 NotifDismissTest")

                self.d.swipe(center_x, center_y, 0, center_y, duration=0.5)
                self.d.sleep(2)
                is_massage_deleted = True
                if self.d(text="NotifDismissTest").exists(3):
                    is_massage_deleted = False
            else:
                print("  [Fail] 找不到 NotifDismissTest")
                self.unlock_device()
                self.d.sleep(1)
                self.click_fail()
                return False

            self.unlock_device()
            self.d.sleep(1)

            pass_btn = self.d(resourceId="com.android.cts.verifier:id/iva_action_button_pass", enabled=True)

            if not pass_btn.wait(1):
                self.d(scrollable=True).scroll.to(resourceId="com.android.cts.verifier:id/iva_action_button_pass",enabled=True)

            if pass_btn.exists and is_massage_deleted:
                print("  [Check] NotifDismissTest 應該被刪除")
                self.d.sleep(1)
                pass_btn.click()
            else:
                print("  [Fail] 滾動到底部仍找不到 Pass 按鈕 2")
                self.click_fail()
                return False

            launch_channel_settings = self.d(text="Launch Channel Settings", enabled=True)
            if not launch_channel_settings.wait(3):
                self.d(scrollable=True).scroll.to(text="Launch Channel Settings", enabled=True)
                self.d.sleep(1)
            launch_channel_settings.click()

            self.d.sleep(1)
            self.settings_in_nav("Lock screen", "Show all notification content")

            retry_back = 0
            while not self.d(resourceId=self.btn_pass).exists() and retry_back < 2:
                self.d.press("back")
                self.d.sleep(1)
                retry_back += 1

            self.d.sleep(2)
            self.d.press("power")
            self.d.sleep(2)
            self.d.press("power")

            notification_dismiss_arrow = self.d(text="NotifDismissTest").right(
                resourceId="android:id/expand_button_pill")
            if notification_dismiss_arrow.exists(2):
                print("  [Check] 在桌面有顯示 NotifDismissTest")
                bounds = notification_dismiss_arrow.info['bounds']

                center_y = (bounds['top'] + bounds['bottom']) // 2
                center_x = (bounds['left'] + bounds['right']) // 2

                print(f"  [Action] 準備刪除 NotifDismissTest")

                self.d.swipe(center_x, center_y, 0, center_y, duration=0.5)
                self.d.sleep(2)
                is_massage_deleted = True
                if self.d(text="NotifDismissTest").exists(3):
                    is_massage_deleted = False

            else:
                print("  [Fail] 找不到 NotifDismissTest")
                self.unlock_device()
                self.d.sleep(1)
                self.click_fail()
                return False

            self.unlock_device()
            self.d.sleep(1)

            pass_btn = self.d(resourceId="com.android.cts.verifier:id/iva_action_button_pass", enabled=True)

            if not pass_btn.wait(1):
                self.d(scrollable=True).scroll.to(resourceId="com.android.cts.verifier:id/iva_action_button_pass",enabled=True)

            if pass_btn.exists and is_massage_deleted:
                print("  [Check] NotifDismissTest 應該被刪除")
                self.d.sleep(1)
                pass_btn.click()
            else:
                print("  [Fail] 滾動到底部仍找不到 Pass 按鈕 3")
                self.click_fail()
                return False

            self.d.sleep(1)
            launch_notification_settings = self.d(text="Launch Notification Settings", enabled=True)
            if not launch_notification_settings.wait(3):
                self.d(scrollable=True).scroll.to(text="Launch Channel Settings", enabled=True)
                self.d.sleep(1)
            launch_notification_settings.click()

            self.d.sleep(1)
            self.settings_in_nav("Sensitive notifications")
            self.d.sleep(1)

            retry_back = 0
            while not self.d(resourceId=self.btn_pass).exists() and retry_back < 2:
                self.d.press("back")
                self.d.sleep(1)
                retry_back += 1

            self.d.sleep(2)
            self.d.press("power")
            self.d.sleep(2)
            self.d.press("power")

            notification_dismiss_arrow = self.d(text="NotifDismissTest").right(
                resourceId="android:id/expand_button_pill")
            if notification_dismiss_arrow.exists(2):
                print("  [Check] 在桌面有顯示 NotifDismissTest")
                bounds = notification_dismiss_arrow.info['bounds']

                center_y = (bounds['top'] + bounds['bottom']) // 2
                center_x = (bounds['left'] + bounds['right']) // 2

                print(f"  [Action] 準備刪除 NotifDismissTest")

                self.d.swipe(center_x, center_y, 0, center_y, duration=0.5)
                self.d.sleep(2)
                is_massage_deleted = False
                if self.d(text="NotifDismissTest").exists(3):
                    is_massage_deleted = True
            else:
                print("  [Fail] 找不到 NotifDismissTest")
                self.unlock_device()
                self.d.sleep(1)
                self.click_fail()
                return False

            self.unlock_device()
            self.d.sleep(1)

            pass_btn = self.d(resourceId="com.android.cts.verifier:id/iva_action_button_pass", enabled=True)

            if not pass_btn.wait(1):
                self.d(scrollable=True).scroll.to(resourceId="com.android.cts.verifier:id/iva_action_button_pass", enabled=True)

            if pass_btn.exists and is_massage_deleted:
                print("  [Check] NotifDismissTest 不應該被刪除")
                self.d.sleep(3)
                pass_btn.click()
            else:
                print("  [Fail] 滾動到底部仍找不到 Pass 按鈕 4")
                self.click_fail()
                return False

            self.remove_screen_lock()
            self.d.sleep(3)

            if self.d(resourceId=self.btn_pass).exists(3):
                self.click_pass()
            else:
                self.click_fail()

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

    def notification_full_screen_intent_test(self):
        self.test_name = "Notification Full Screen Intent Test"

        # self.set_screen_lock()

        try:
            if not self.scroll_and_click(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                return False

            self.d.sleep(1)
            launch_notification_settings = self.d(text="Launch Notification Settings", enabled=True)
            if launch_notification_settings.exists(10):
                launch_notification_settings.click()
                self.d.sleep(1)
                self.settings_in_nav("Sensitive notifications")
                sensitive_notifications_switch = self.d(text="Sensitive notifications").right(className="android.widget.Switch")
                if not sensitive_notifications_switch.info.get("checked"):
                    sensitive_notifications_switch.click()
                self.d.sleep(1)

                retry_back = 0
                while not self.d(resourceId=self.btn_pass).exists() and retry_back < 2:
                    self.d.press("back")
                    self.d.sleep(1)
                    retry_back += 1

            self.d.sleep(1)
            i_m_done = self.d(text="I'm done",enabled=True)
            if not i_m_done.wait(1):
                self.d(scrollable=True).scroll.to(text="I'm done",enabled=True)

            if i_m_done.exists():
                i_m_done.click()
            else:
                print("  [Fail] 畫面上未顯示 I'm done 按鈕可點擊，測試失敗")
                self.click_fail()
                return False

            self.d.sleep(1)

            # 按下電源鍵，觸發 Full Screen Intent
            self.d.press("power")

            # 確認是否有順利叫出 Full screen intent 畫面
            intent_text = self.d(textContains="This page is a full screen intent")
            if intent_text.exists(5):
                print("  [Action] 成功觸發 Full Screen Intent")

                retry_back = 0
                while intent_text.exists(2) and retry_back < 2:
                    self.d.press("home")
                    self.d.sleep(1)
                    retry_back += 1

                if not intent_text.exists(1):
                    self.unlock_device()
                    self.open_ctsv_from_recents()
                    self.d.press("back")

                self.d.sleep(2)

                # 驗證是否順利回到 CTS 畫面並可以點擊 PASS
                pass_btn = self.d(resourceId="com.android.cts.verifier:id/iva_action_button_pass", enabled=True)

                # 這裡必須加上 timeout，不要用瞬間判定，否則解鎖慢一點點就會誤判失敗
                if pass_btn.exists(3):
                    print("  [Check] full screen intent 驗證正常，點擊 Pass")
                    pass_btn.click()
                else:
                    print("  [Fail] full screen intent 驗證失敗 (解鎖後找不到可點擊的 Pass 按鈕)")
                    self.click_fail()
                    return False

            else:
                print("  [Fail] 按下 Power 鍵後，未偵測到 Full Screen Intent 畫面")
                self.click_fail()
                return False

            launch_lock_screen_settings = self.d(text="Launch Lock Screen Settings", enabled=True)
            if not launch_lock_screen_settings.wait(1):
                self.d(scrollable=True).scroll.to(text="Launch Lock Screen Settings", enabled=True)

            if launch_lock_screen_settings.exists():
                launch_lock_screen_settings.click()
                self.d.sleep(1)
                self.settings_in_nav("Always show time and info")
                lock_screen_switch = self.d(text="Always show time and info").right(className="android.widget.Switch")
                if lock_screen_switch.info.get("checked"):
                    lock_screen_switch.click()
                self.d.sleep(1)

                retry_back = 0
                while not self.d(resourceId=self.btn_pass).exists() and retry_back < 2:
                    self.d.press("back")
                    self.d.sleep(1)
                    retry_back += 1
            else:
                print("  [Fail] 畫面上未顯示Launch Lock Screen 按鈕可點擊，測試失敗")
                self.click_fail()
                return False

            self.d.sleep(1)
            i_m_done = self.d(text="I'm done", enabled=True)
            if not i_m_done.wait(1):
                self.d(scrollable=True).scroll.to(text="I'm done", enabled=True)

            if i_m_done.exists():
                i_m_done.click()
            else:
                print("  [Fail] 畫面上未顯示 I'm done 按鈕可點擊，測試失敗")
                self.click_fail()
                return False

            self.d.sleep(1)

            self.d.press("power")

            # 確認是否有順利叫出 Full screen intent 畫面
            intent_text = self.d(textContains="This page is a full screen intent")
            if intent_text.exists(5):
                print("  [Action] 成功觸發 Full Screen Intent")

                retry_back = 0
                while intent_text.exists(2) and retry_back < 2:
                    self.d.press("home")
                    self.d.sleep(1)
                    retry_back += 1

                if not intent_text.exists(1):
                    self.unlock_device()
                    self.open_ctsv_from_recents()
                    self.d.press("back")

                self.d.sleep(2)

            pass_btn = self.d(resourceId="com.android.cts.verifier:id/iva_action_button_pass", enabled=True)
            if pass_btn.exists:
                print("  [Check] full screen intent 驗證正常")
                self.d.sleep(1)
                pass_btn.click()
            else:
                print("  [Fail] full screen intent 驗證失敗")
                self.click_fail()
                return False

            launch_lock_screen_settings = self.d(text="Launch Lock Screen Settings", enabled=True)
            if not launch_lock_screen_settings.wait(1):
                self.d(scrollable=True).scroll.to(text="Launch Lock Screen Settings", enabled=True)

            if launch_lock_screen_settings.exists():
                launch_lock_screen_settings.click()
                self.d.sleep(1)
                self.settings_in_nav("Always show time and info")
                lock_screen_switch = self.d(text="Always show time and info").right(className="android.widget.Switch")
                if not lock_screen_switch.info.get("checked"):
                    lock_screen_switch.click()
                self.d.sleep(1)

                retry_back = 0
                while not self.d(resourceId=self.btn_pass).exists() and retry_back < 2:
                    self.d.press("back")
                    self.d.sleep(1)
                    retry_back += 1
            else:
                print("  [Fail] 畫面上未顯示Launch Lock Screen 按鈕可點擊，測試失敗")
                self.click_fail()
                return False

            i_m_done = self.d(text="I'm done", enabled=True)
            if not i_m_done.wait(1):
                self.d(scrollable=True).scroll.to(text="I'm done",enabled=True)

            if i_m_done.exists():
                i_m_done.click()
            else:
                print("  [Fail] 畫面上未顯示 I'm done 按鈕可點擊，測試失敗")
                self.click_fail()
                return False

            self.d.sleep(1)

            # 按下電源鍵，觸發 Full Screen Intent
            self.d.press("power")

            # 確認是否有順利叫出 Full screen intent 畫面
            intent_text = self.d(textContains="This page is a full screen intent")
            if intent_text.exists(5):
                print("  [Action] 成功觸發 Full Screen Intent")

                retry_back = 0
                while intent_text.exists(2) and retry_back < 2:
                    self.d.press("home")
                    self.d.sleep(1)
                    retry_back += 1

                if not intent_text.exists(1):
                    self.unlock_device()
                    self.open_ctsv_from_recents()
                    self.d.press("back")

                self.d.sleep(2)

                pass_btn = self.d(resourceId="com.android.cts.verifier:id/iva_action_button_pass", enabled=True)

                if pass_btn.exists(3):
                    print("  [Check] full screen intent 驗證正常，點擊 Pass")
                    pass_btn.click()
                else:
                    print("  [Fail] full screen intent 驗證失敗 (解鎖後找不到可點擊的 Pass 按鈕)")
                    self.click_fail()
                    return False

            else:
                print("  [Fail] 按下 Power 鍵後，未偵測到 Full Screen Intent 畫面")
                self.click_fail()
                return False

            launch_security_settings = self.d(text="Launch Security Settings", enabled=True)
            if not launch_security_settings.wait(1):
                self.d(scrollable=True).scroll.to(text="Launch Security Settings", enabled=True)

            if launch_security_settings.exists():
                launch_security_settings.click()
                self.d.sleep(1)
                allow_full_screen_switch = self.d(text="Allow full screen notifications from this app").right(className="android.widget.Switch")
                allow_full_screen_switch.click()
                self.d.sleep(1)

                retry_back = 0
                while not self.d(resourceId=self.btn_pass).exists() and retry_back < 2:
                    self.d.press("back")
                    self.d.sleep(1)
                    retry_back += 1
            else:
                print("  [Fail] 畫面上未顯示Launch Security Settings 按鈕可點擊，測試失敗")
                self.click_fail()
                return False

            i_m_done = self.d(text="I'm done",enabled=True)
            if not i_m_done.wait(1):
                self.d(scrollable=True).scroll.to(text="I'm done",enabled=True)

            if i_m_done.exists():
                i_m_done.click()
            else:
                print("  [Fail] 畫面上未顯示 I'm done 按鈕可點擊，測試失敗")
                self.click_fail()
                return False

            self.d.sleep(1)

            intent_text = self.d(text="Fsi Notif Content Fsi Notif Content Fsi Notif Content   Fsi Notif Content Fsi Notif Content Fsi Notif Content")
            if intent_text.exists(5):
                print("  [Action] 成功觸發 Heads Up 通知")
                start_time = time.time()

                # 只要還沒滿 60 秒，就持續在迴圈裡檢查
                while time.time() - start_time < 60:
                    # 如果中途通知消失了 (exists 回傳 False)
                    if not intent_text.exists():
                        elapsed = int(time.time() - start_time)
                        print(f"  [Fail] Heads Up 通知僅顯示 {elapsed} 秒。")
                        self.click_fail()
                        return False

                    time.sleep(1)
                print("  [Success] Heads Up 通知顯示滿 60 秒。")
                pass_btn = self.d(resourceId="com.android.cts.verifier:id/iva_action_button_pass", enabled=True)

                if pass_btn.exists(3):
                    print("  [Check] full screen intent 驗證正常，點擊 Pass")
                    pass_btn.click()
                else:
                    print("  [Fail] full screen intent 驗證失敗 (解鎖後找不到可點擊的 Pass 按鈕)")
                    self.click_fail()
                    return False
            else:
                print("  [Fail] 沒有觸發 Heads Up 通知")
                self.click_fail()
                return False

            launch_lock_screen_settings = self.d(text="Launch Lock Screen Settings", enabled=True)
            if not launch_lock_screen_settings.wait(1):
                self.d(scrollable=True).scroll.to(text="Launch Lock Screen Settings", enabled=True)

            if launch_lock_screen_settings.exists():
                launch_lock_screen_settings.click()
                self.settings_in_nav("Always show time and info")
                lock_screen_switch = self.d(text="Always show time and info").right(className="android.widget.Switch")
                if not lock_screen_switch.info.get("checked"):
                    lock_screen_switch.click()
                self.d.sleep(1)

                retry_back = 0
                while not self.d(resourceId=self.btn_pass).exists() and retry_back < 2:
                    self.d.press("back")
                    self.d.sleep(1)
                    retry_back += 1
            else:
                print("  [Fail] 畫面上未顯示 Launch Lock Screen Settings 按鈕可點擊，測試失敗")
                self.click_fail()
                return False

            i_m_done = self.d(text="I'm done", enabled=True)
            if not i_m_done.wait(1):
                self.d(scrollable=True).scroll.to(text="I'm done", enabled=True)

            if i_m_done.exists():
                i_m_done.click()
            else:
                print("  [Fail] 畫面上未顯示 I'm done 按鈕可點擊，測試失敗")
                self.click_fail()
                return False

            self.d.sleep(1)
            self.d.press("power")

            intent_text = self.d(text="Fsi Notif Content Fsi Notif Content Fsi Notif Content   Fsi Notif Content Fsi Notif Content Fsi Notif Content")
            if intent_text.exists(5):
                print("  [Action] 成功觸發 Heads Up 通知")
                retry_back = 0
                while intent_text.exists(2) and retry_back < 2:
                    self.d.press("home")
                    self.d.sleep(1)
                    retry_back += 1

                if not intent_text.exists(1):
                    self.unlock_device()
                    self.open_ctsv_from_recents()
                    self.d.press("back")

                self.d.sleep(2)

            else:
                print("  [Fail] 沒有觸發 Heads Up 通知")
                self.click_fail()
                return False

            pass_btn = self.d(resourceId="com.android.cts.verifier:id/iva_action_button_pass", enabled=True)
            if pass_btn.exists:
                print("  [Check] NotifFsiTest 通知跳出驗證正常")
                self.d.sleep(1)
                pass_btn.click()
            else:
                print("  [Fail] NotifFsiTest 通知跳出驗證失敗")
                self.click_fail()
                return False

            launch_lock_screen_settings = self.d(text="Launch Lock Screen Settings", enabled=True)
            if not launch_lock_screen_settings.wait(1):
                self.d(scrollable=True).scroll.to(text="Launch Lock Screen Settings", enabled=True)

            if launch_lock_screen_settings.exists():
                launch_lock_screen_settings.click()
                self.settings_in_nav("Always show time and info")
                lock_screen_switch = self.d(text="Always show time and info").right(className="android.widget.Switch")
                if lock_screen_switch.info.get("checked"):
                    lock_screen_switch.click()
                self.d.sleep(1)

                retry_back = 0
                while not self.d(resourceId=self.btn_pass).exists() and retry_back < 2:
                    self.d.press("back")
                    self.d.sleep(1)
                    retry_back += 1
            else:
                print("  [Fail] 畫面上未顯示 Launch Lock Screen Settings 按鈕可點擊，測試失敗")
                self.click_fail()
                return False

            i_m_done = self.d(text="I'm done", enabled=True)
            if not i_m_done.wait(1):
                self.d(scrollable=True).scroll.to(text="I'm done", enabled=True)

            if i_m_done.exists():
                i_m_done.click()
            else:
                print("  [Fail] 畫面上未顯示 I'm done 按鈕可點擊，測試失敗")
                self.click_fail()
                return False

            self.d.sleep(1)
            self.d.press("power")

            intent_text = self.d(
                text="Fsi Notif Content Fsi Notif Content Fsi Notif Content   Fsi Notif Content Fsi Notif Content Fsi Notif Content")
            if intent_text.exists(5):
                print("  [Action] 成功觸發 Heads Up 通知")
                retry_back = 0
                while intent_text.exists(2) and retry_back < 2:
                    self.d.press("home")
                    self.d.sleep(1)
                    retry_back += 1

                if not intent_text.exists(1):
                    self.unlock_device()
                    self.open_ctsv_from_recents()
                    self.d.press("back")

                self.d.sleep(2)

            else:
                print("  [Fail] 沒有觸發 Heads Up 通知")
                self.click_fail()
                return False

            pass_btn = self.d(resourceId="com.android.cts.verifier:id/iva_action_button_pass", enabled=True)
            if pass_btn.exists:
                print("  [Check] NotifFsiTest 通知跳出驗證正常")
                self.d.sleep(1)
                pass_btn.click()
            else:
                print("  [Fail] NotifFsiTest 通知跳出驗證失敗")
                self.click_fail()
                return False


            if self.d(resourceId=self.btn_pass).exists(3):
                self.click_pass()
            else:
                self.click_fail()

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

        finally:
            self.unlock_device()


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

    task = Notification()
    try:
        if args.retry:
            fail_list = json.loads(args.retry)
            task.run_specific_tests(fail_list)
        else:
            # task.bubble_notification_tests()
            # task.ca_cert_notification_test()
            # task.ca_cert_notification_on_boot_test()
            # task.condition_provider_test()
            # task.notification_dismiss_test()
            task.notification_full_screen_intent_test()
    finally:
        try:
            task.d.stop_uiautomator()
        except:
            pass







