import uiautomator2 as u2

class CtsVerifier:
    def __init__(self, serial="SGG6B7500003"):
        # 1. 自動連線
        self.d = u2.connect(serial)

        # 2. 預先定義共用按鈕 (這裡用 resourceId，因為這是全 App 通用的)
        self.btn_pass = "com.android.cts.verifier:id/pass_button"
        self.btn_fail = "com.android.cts.verifier:id/fail_button"

        self.d.watcher("AutoClicker").when('//*[@text="OK"]').click()
        self.d.watcher.start()



    def scroll_and_click(self, target_text):
        print(f"  [Nav] Searching for '{target_text}' ")

        # 1. 先看一眼當前畫面有沒有
        if self.d(text=target_text).exists:
            self.d(text=target_text).click()
            print(f"  [Nav] Found '{target_text}'.")
            return True

        if not self.d(scrollable=True).exists:
            print("  [Error] 找不到可滾動列表")
            return False

        scroller = self.d(scrollable=True)

        for i in range(30):
            # forward() 回傳 True 代表還有路可以滑，False 代表到底了
            can_scroll_more = scroller.scroll.forward()

            # 每次滑完立刻檢查
            if self.d(text=target_text).exists:
                self.d(text=target_text).click()
                print(f"  [Nav] Found '{target_text}'")
                return True

            if not can_scroll_more:
                break

        for i in range(30):
            can_scroll_more = scroller.scroll.backward()

            if self.d(text=target_text).exists:
                self.d(text=target_text).click()
                print(f"  [Nav] Found '{target_text}'")
                return True

            # 如果回傳 False，代表到頂了
            if not can_scroll_more:
                break

        print(f"  [Error] Search failed. '{target_text}' not found.")
        return False

    def click_pass(self):
        if self.d(resourceId=self.btn_pass).exists(timeout=2):
            self.d(resourceId=self.btn_pass).click()
        else:
            print("[Error] 無法點擊 Pass 按鈕")

    def click_fail(self):
        if self.d(resourceId=self.btn_fail).exists(timeout=2):
            self.d(resourceId=self.btn_fail).click()
        else:
            print("[Error] 無法點擊 Fail 按鈕")

    def enter_subtest(self, text_name):
        """進入子測項的通用方法"""
        if self.d(text=text_name).exists:
            self.d(text=text_name).click()
            print(f"\n>>> Entering Test: {text_name}")
            return True
        else:
            print(f"[Error] Cannot find menu item: {text_name}")
            return False

    def go_back_to_list(self):
        """
        [災難復原]
        強制停止 CTS Verifier 並重新啟動，確保回到乾淨的列表頁。
        適用於 Exception 發生後的 finally 區塊。
        """
        package_name = "com.android.cts.verifier"

        print(f"  [Recovery] 偵測到異常或結束，正在重啟 {package_name}...")

        # 1. 強制殺掉 App
        self.d.app_stop(package_name)

        # 2. 稍微緩衝一下確保 Process 已死透
        self.d.sleep(1)

        # 3. 重新啟動 App
        self.d.app_start(package_name)

        # 4. 等待列表出現，確認重啟成功
        if self.d(text="CTS Verifier").wait(timeout=10):
            print("  [Recovery] 重啟成功，已回到列表頁。")
            self.d.sleep(2)
        else:
            print("  [Recovery] 重啟後未偵測到列表首頁，請檢查。")
            return


    def set_screen_lock(self, mode="Pattern"):
        """ 設定螢幕鎖定 """
        print(f"  [Security] 正在設定螢幕鎖定為: {mode}...")
        self.d.shell("am start -a android.settings.SECURITY_SETTINGS")
        self.d.sleep(1)

        if not self.d(text="Device unlock").exists:
            self.d(scrollable=True).scroll.to(text="Device unlock")
        self.d.sleep(1)

        if self.d(text="Device unlock").exists:
            self.d(text="Device unlock").click()
        elif self.d(textContains="unlock").exists:
            self.d(textContains="unlock").click()
        else:
            print("  [Error] 找不到 'Device unlock' 選項")
            return

        self.d.sleep(1)
        if not self.d(text="Screen lock").exists:
            self.d(scrollable=True).scroll.to(text="Screen lock")

        if self.d(text="Screen lock").exists:
            self.d(text="Screen lock").click()
        else:
            print("  [Error] 找不到 'Screen lock' 選項")
            return

        self.d.sleep(1)

        # === 處理不同模式 ===
        if mode == "Swipe":
            self.d(text="Swipe").click()
            if self.d(textContains="YES").exists:
                self.d(textContains="YES").click()
            elif self.d(textContains="Remove").exists:
                self.d(textContains="Remove").click()

        elif mode == "Pattern":
            self.d(text="Pattern").click()
            self.d.sleep(1)
            self._draw_l_shape_pattern()  # 第一次
            self.d(text="Next").click()
            self.d.sleep(1)
            self._draw_l_shape_pattern()  # 第二次
            self.d(text="Confirm").click()

        elif mode == "PIN":
            self.d(text="PIN").click()
            self.d.sleep(1)
            self._input_text_lock("1234")
            self.d(text="Next").click()
            self.d.sleep(1)
            self._input_text_lock("1234")
            self.d(text="Confirm").click()

        elif mode == "Password":
            self.d(text="Password").click()
            self.d.sleep(1)
            self._input_text_lock("Foxconn123")
            self.d(text="Next").click()
            self.d.sleep(1)
            self._input_text_lock("Foxconn123")
            self.d(text="Confirm").click()

        self.d.sleep(1)
        if self.d(text="Done").exists:
            self.d(text="Done").click()

        print(f"  [Security] 設定 {mode} 完成")
        self.d.press("home")

    def unlock_device(self):
        """ 自動判斷並解鎖回到桌面 """
        print("  [System] 檢測到螢幕鎖定，嘗試解鎖...")

        if not self.d.info.get('screenOn'):
            self.d.screen_on()
            self.d.sleep(1)

        print("    -> 滑動解鎖頁面 (Swipe Up)...")
        self.d.swipe(0.5, 0.8, 0.5, 0.3)
        self.d.sleep(0.5)

        if not (self.d(resourceId="com.android.systemui:id/lockPatternView").exists or \
                self.d(text="Emergency").exists or \
                self.d(text="緊急呼叫").exists):
            self.d.swipe(0.5, 0.8, 0.5, 0.3)
            self.d.sleep(1)

        # 識別並解鎖
        if self.d(resourceId="com.android.systemui:id/lockPatternView").exists:
            print("    [Unlock] 偵測到圖形鎖，繪製 L 型...")
            self._draw_l_shape_pattern_lockscreen()

        elif self.d(resourceId="com.android.systemui:id/key1").exists or self.d(text="1").exists:
            print("    [Unlock] 偵測到 PIN 碼鍵盤，輸入 1234...")
            self._click_pin_buttons("1234")
            self.d.sleep(0.5)
            if self.d(resourceId="com.android.systemui:id/key_enter").exists:
                self.d(resourceId="com.android.systemui:id/key_enter").click()
            elif self.d(description="Enter").exists:
                self.d(description="Enter").click()

        elif self.d(className="android.widget.EditText").exists:
            print("    [Unlock] 偵測到密碼輸入框，輸入 Foxconn123...")
            self.d.send_keys("Foxconn123")
            self.d.sleep(0.5)
            self.d.press("enter")
        else:
            print("    [Info] 似乎已解鎖，或無密碼 (Swipe Only)。")

        self.d.sleep(1)
        print("  [System] 解鎖動作完成")

    def remove_screen_lock(self):
        """ 解除螢幕鎖定 (回到 None) """
        print("  [Security] 正在移除螢幕鎖定 ...")
        self.d.shell("am start -a android.settings.SECURITY_SETTINGS")
        self.d.sleep(1)

        if not self.d(text="Device unlock").exists:
            self.d(scrollable=True).scroll.to(text="Device unlock")
        if self.d(text="Device unlock").exists:
            self.d(text="Device unlock").click()
        self.d.sleep(1)

        if not self.d(text="Screen lock").exists:
            self.d(scrollable=True).scroll.to(text="Screen lock")
        if self.d(text="Screen lock").exists:
            self.d(text="Screen lock").click()
        else:
            return

        self.d.sleep(1)

        # --- 處理身份驗證 ---
        if self.d(resourceId="com.android.settings:id/lockPattern").exists:
            print("  [Auth] 偵測到圖形鎖...")
            self._draw_l_shape_pattern()
        elif self.d(textContains="PIN").exists:
            print("  [Auth] 偵測到 PIN 碼要求...")
            self._input_text_lock("1234")
            self.d.press("enter")
        elif self.d(textContains="password").exists or self.d(textContains="Password").exists:
            print("  [Auth] 偵測到密碼要求...")
            self._input_text_lock("Foxconn123")
            self.d.press("enter")

        self.d.sleep(1)

        # 設定為 None 並處理確認彈窗
        if self.d(text="None").exists:
            self.d(text="None").click()
            if self.d(textContains="Delete").wait(timeout=2):
                if self.d(resourceId="android:id/button1").exists:
                    self.d(resourceId="android:id/button1").click()
                elif self.d(text="Delete").exists:
                    self.d(text="Delete").click()

        print("  [Security] 螢幕鎖定已移除 (None)")
        self.d.press("home")

    # ==========================================
    #  [正式 Method] 所有的 Helper 必須在 Class 層級
    # ==========================================

    def _draw_l_shape_pattern_lockscreen(self):
        """ 專門針對 SystemUI (鎖定畫面) 的圖形鎖繪製 """
        pattern_view = self.d(resourceId="com.android.systemui:id/lockPatternView")
        if not pattern_view.exists:
            pattern_view = self.d(className="com.android.internal.widget.LockPatternView")

        if pattern_view.exists:
            rect = pattern_view.info['bounds']
            left, top, right, bottom = rect['left'], rect['top'], rect['right'], rect['bottom']
            w, h = (right - left) / 3, (bottom - top) / 3
            p1 = (left + w * 0.5, top + h * 0.5)
            p4 = (left + w * 0.5, top + h * 1.5)
            p7 = (left + w * 0.5, top + h * 2.5)
            p8 = (left + w * 1.5, top + h * 2.5)
            p9 = (left + w * 2.5, top + h * 2.5)
            self.d.swipe_points([p1, p4, p7, p8, p9], duration=0.4)

    def _click_pin_buttons(self, pin_code):
        """ 模擬手指點擊 PIN 碼按鈕 """
        for char in pin_code:
            if self.d(resourceId=f"com.android.systemui:id/key{char}").exists:
                self.d(resourceId=f"com.android.systemui:id/key{char}").click()
            elif self.d(text=char).exists:
                self.d(text=char).click()
            self.d.sleep(0.1)

    def _input_text_lock(self, text):
        """ 處理鎖定畫面/設定頁面的文字輸入 """
        focused = self.d(focused=True)
        if focused.exists:
            focused.set_text(text)
        else:
            self.d.send_keys(text)

    def _draw_l_shape_pattern(self):
        """ 繪製 L 型圖形鎖 (設定頁面版) """
        pattern_view = self.d(resourceId="com.android.settings:id/lockPattern")
        if pattern_view.exists:
            info = pattern_view.info['bounds']
            left, top, right, bottom = info['left'], info['top'], info['right'], info['bottom']
            w, h = (right - left) / 3, (bottom - top) / 3
            p1 = (left + w * 0.5, top + h * 0.5)
            p4 = (left + w * 0.5, top + h * 1.5)
            p7 = (left + w * 0.5, top + h * 2.5)
            p8 = (left + w * 1.5, top + h * 2.5)
            p9 = (left + w * 2.5, top + h * 2.5)
            self.d.swipe_points([p1, p4, p7, p8, p9], duration=0.4)

    def click_final_pass(self):
        """ 當所有子測項都通過後，點擊主畫面左下角的 Pass 按鈕 """
        pass_btn = self.d(resourceId="com.android.cts.verifier:id/pass_button", enabled=True)
        fail_btn = self.d(resourceId="com.android.cts.verifier:id/fail_button")

        if pass_btn.wait(timeout=3):
            pass_btn.click()
        else:
            fail_btn.click()
