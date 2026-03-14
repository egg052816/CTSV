import uiautomator2 as u2
import os
import time
import subprocess
import sys
import hashlib

sys.stdout.reconfigure(encoding='utf-8')

class CtsVerifier:
    def __init__(self):

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.serial_file = os.path.join(self.base_dir, "current_serial.txt")
        self.serial = self._get_serial_from_file()
        print(f"\n  [Init] 正在連接裝置: {self.serial} ...")

        # 2. 使用重試機制連線，取代原本的 u2.connect(self.serial)

        self.d = self._connect_device_with_retry()

        self.os_version = self.d.device_info['version']
        print(f"  [Info] 目前測試設備的版本為: Android {self.os_version}")

        # 設定全域等待時間
        self.d.wait_timeout = 10.0

        # 設定testcase_name名稱
        self.test_name = "Unknown Test"

        # 3. 預先定義共用按鈕 (這裡用 resourceId，因為這是全 App 通用的)
        self.btn_pass = "com.android.cts.verifier:id/pass_button"
        self.btn_fail = "com.android.cts.verifier:id/fail_button"

        self.d.watcher("AutoClicker").when('//*[@text="OK"]').click()
        self.d.watcher("AutoClicker").when('//*[@text="Got it"]').click()
        self.d.watcher("AutoClicker").when('//*[@text="No thanks"]').click()
        # self.d.watcher("AutoClicker").when('//*[@text="Confirm"]').click() # 設定密碼會有問題
        self.d.watcher("AutoClicker").when('//*[@text="ALWAYS"]').click()
        # self.d.watcher("AutoClicker").when('//*[@text="Turn on location"]').click()
        self.d.watcher("AutoClicker").when('//*[@text="Dismiss"]').click()
        self.d.watcher.start()

    def scroll_and_click(self, target_text):

        self.test_name = target_text
        # 設定最大重試次數 (防止無限迴圈)
        max_retries = 3

        for attempt in range(max_retries):
            try:
                # === 1. 快速檢查當前畫面 ===
                if self.d(text=target_text).exists:
                    self.d(text=target_text).click()
                    print(f"\n  [TestCase] Searching for:'{target_text}'")
                    return True

                # 檢查是否有捲軸，沒有捲軸且沒找到就是失敗
                if not self.d(scrollable=True).exists:
                    print("  [Fail] 頁面不可滾動且未發現目標。")
                    return False

                # 取得捲動器物件
                scroller = self.d(scrollable=True)

                # === 2. 使用原生方法向下搜尋 (更準、更快) ===
                # scroll.to 會自動邊滑邊找，直到找到 or 到底為止
                if scroller.scroll.to(text=target_text):
                    self.d(text=target_text).click()
                    print(f"\n  [TestCase] Found : '{target_text}'")
                    return True

                # === 3. 如果到底還沒找到，直接回到頂部 ===
                # 避免像原本那樣慢慢滑回去，直接跳回最上面
                print("    -> 到底部未發現，正在回到頂部...")
                scroller.scroll.toBeginning(steps=50)  # steps多一點滑比較穩

                # 回頂部後再看最後一次
                if self.d(text=target_text).exists:
                    self.d(text=target_text).click()
                    print(f"  [Nav] Found (at Top): '{target_text}'")
                    return True

                print(f"  [Fail] Search failed. '{target_text}' not found.")
                return False

            except Exception as e:
                # === 4. 這裡就是救命的關鍵 ===
                # 如果滑動或點擊過程斷線，會進來這裡，而不是直接 Crash
                print(f"  [Warning] 搜尋過程發生異常 (Attempt {attempt + 1}/{max_retries}): {e}")

                if attempt < max_retries - 1:
                    print("    -> 正在嘗試重新連線並重試...")
                    self._repair_environment()  # 1. 殺掉手機端服務/重啟ADB
                    self.d = self._connect_device_with_retry()  # 2. 重新建立連線物件
                    # 迴圈會繼續 (continue)，重新執行一次搜尋
                else:
                    print("  [Fail] 失敗，停止搜尋。")
                    raise e  # 真的救不回來才報錯中止

        return False

    def click_pass(self):
        if self.d(resourceId=self.btn_pass).exists(timeout=3):
            print(f"  [Pass] {self.test_name} 測試成功" )
            self.d(resourceId=self.btn_pass).click()
        else:
            print("  [Fail] 無法點擊 Pass 按鈕")

            package_name = "com.android.cts.verifier"
            # 這是 CTS Verifier 的主進入點 Activity
            main_activity = "com.android.cts.verifier/.CtsVerifierActivity"
            cmd = f"sh -c 'am force-stop {package_name}; am start -n {main_activity} -W -f 0x10008000'"
            self.d.shell(cmd)

    def click_fail(self):
        if self.d(resourceId=self.btn_fail).exists(timeout=3):
            print(f"  [Fail] {self.test_name} 測試異常，判定失敗" )
            self.d(resourceId=self.btn_fail).click()
        else:
            print("  [Fail] 無法點擊 Fail 按鈕")

            package_name = "com.android.cts.verifier"
            # 這是 CTS Verifier 的主進入點 Activity
            main_activity = "com.android.cts.verifier/.CtsVerifierActivity"
            cmd = f"sh -c 'am force-stop {package_name}; am start -n {main_activity} -W -f 0x10008000'"
            self.d.shell(cmd)

    def enter_subtest(self, text_name):
        """進入子測項的通用方法"""

        if self.d(text=text_name).exists:
            self.d(text=text_name).click()
            print(f"\n>>> Entering Test: {text_name}")
            return True
        else:
            print(f"  [Fail] 找不到子測項 {text_name}")
            return False

    def byod_enter_subtest(self, text_name):

        # 鎖定下方的滾動區域 (instance=1 通常是下方的列表容器)
        # 或者直接指定 className="android.widget.ListView"
        sub_list = self.d(scrollable=True, instance=1)

        if not sub_list.exists:
            # 如果 instance=1 不存在，退回用 instance=0
            sub_list = self.d(scrollable=True, instance=0)

        try:
            # 使用 scroll.to 直接滾動到目標文字出現
            if sub_list.scroll.to(text=text_name):
                self.d(text=text_name).click()
                print(f"\n>>> Entering Test: {text_name}")
                return True
        except Exception as e:
            print(f"  [Nav] 滾動尋找 {text_name} 失敗: {e}")

        # 備案：如果 scroll.to 沒反應，手動強制下滑搜尋
        for _ in range(5):
            if self.d(text=text_name).exists:
                self.d(text=text_name).click()
                return True
            # 在螢幕下方 1/3 處執行向上滑動手勢
            w, h = self.d.window_size()
            self.d.swipe(w * 0.5, h * 0.8, w * 0.5, h * 0.4)

        return False

    def go_back_to_list(self):

        package_name = "com.android.cts.verifier"

        print(f"  [Recovery] 偵測到異常或結束，正在重啟 {package_name}...")

        package_name = "com.android.cts.verifier"
        # 這是 CTS Verifier 的主進入點 Activity
        main_activity = "com.android.cts.verifier/.CtsVerifierActivity"

        self.d.shell("cmd statusbar collapse")
        self.d.sleep(1)
        print(f"  [Recovery] 正在重啟...")

        # === 核心修改 ===
        # 使用 sh -c 一次執行兩條指令：
        # 1. am force-stop: 強制殺掉 App
        # 2. am start:
        #    -n: 指定 Component (App/Activity)
        #    -W: 等待啟動完成 (Wait)
        #    -f 0x10008000: 這是關鍵 Flag (FLAG_ACTIVITY_NEW_TASK | FLAG_ACTIVITY_CLEAR_TASK)
        #       它的作用是：不管之前卡在哪一頁，全部清空，重新建立一個全新的首頁。

        cmd = f"sh -c 'am force-stop {package_name}; am start -n {main_activity} -W -f 0x10008000'"
        self.d.shell(cmd)

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

        self.d.shell("am force-stop com.android.settings")
        self.d.sleep(1)
        self.d.shell("am start -W -a android.settings.SECURITY_SETTINGS -f 0x10008000")
        self.d.sleep(3)

        target_layout = self.d(className="android.widget.LinearLayout", clickable=True).child(text="Device unlock")

        found_unlock = False
        for _ in range(8):  # 最多嘗試滑動 8 次
            if target_layout.exists:
                found_unlock = True
                break

            print("  [Nav] 目前未發現 'Device unlock'...")
            # 獲取螢幕尺寸來計算滑動座標
            w, h = self.d.window_size()
            # 從螢幕 60% 高度滑到 40% 高度，steps=50 代表滑動速度極慢，減少慣性
            self.d.swipe(0.5 * w, 0.6 * h, 0.5 * w, 0.4 * h, steps=50)
            self.d.sleep(1)

        if found_unlock:
            print("  [Click] 找到 Device unlock，執行點擊")
            target_layout.click()
        else:
            print("  [Fail] 找不到 'Device unlock' 選項")
            return

        self.d.sleep(1)

        found_lock = False
        for _ in range(5):
            if self.d(text="Screen lock").exists:
                found_lock = True
                break

            print("    [Nav] 未發現 'Screen lock'，微距滑動...")
            w, h = self.d.window_size()
            self.d.swipe(0.5 * w, 0.6 * h, 0.5 * w, 0.4 * h, steps=50)
            self.d.sleep(1)

        if found_lock:
            self.d(text="Screen lock").click()
        else:
            print("    [Fail] 找不到 'Screen lock' 選項")
            return

        self.d.sleep(1.5)

        auth_title = self.d(resourceId="com.android.settings:id/suc_layout_title")

        # 判斷條件：標題存在且包含 Pattern，或者直接看到了九宮格 (lockPattern)
        # 使用 exists(timeout=2) 稍微等一下，如果沒出現就代表不需要驗證，繼續往下跑
        if (auth_title.exists(timeout=2) and "pattern" in auth_title.get_text().lower()) or \
                self.d(resourceId="com.android.settings:id/lockPattern").exists:
            print("  [Auth] 偵測到 'Confirm your pattern' 要求，輸入舊圖形鎖(L)...")
            self._draw_l_shape_pattern()

            # 畫完之後，給它一點時間跳轉到選擇清單
            self.d.sleep(1.5)

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
        self.open_ctsv_from_recents()

    def unlock_device(self):
        """ 自動判斷並解鎖回到桌面 """
        print("  [System] 檢測到螢幕鎖定，嘗試解鎖...")

        if not self.d.info.get('screenOn'):
            self.d.screen_on()
            self.d.sleep(1)

        max_retries = 5
        retry_count = 0

        print("    -> 滑動解鎖頁面 (Swipe Up)...")
        self.d.swipe(0.5, 0.8, 0.5, 0.3)
        self.d.sleep(0.5)

        while retry_count < max_retries:
            # 檢查是否已看到密碼輸入介面
            has_pattern = self.d(resourceId="com.android.systemui:id/lockPatternView").exists
            has_emergency = self.d(text="Emergency").exists
            has_pin = self.d(resourceId="com.android.systemui:id/key1").exists or self.d(text="1").exists

            if has_pattern or has_emergency or has_pin:
                print(f"    -> [Success] 已進入解鎖介面 (嘗試第 {retry_count} 次)")
                break

            print(f"    -> 滑動解鎖頁面 (第 {retry_count + 1} / {max_retries} 次 Swipe Up)...")
            if retry_count == 0:
                os.system(f"adb -s {self.serial} shell input keyevent 82")
            else:
                self.d.swipe(0.5, 0.8, 0.5, 0.2, steps=20)
            self.d.sleep(1)  # 給系統一點轉場反應時間

            if retry_count % 2:
                self.d.click(0.5, 0.5)

            retry_count += 1

        if retry_count >= max_retries:
            print("  [Fail] 已達到最大滑動次數,螢幕解鎖失敗")

        # 識別並解鎖
        if self.d(resourceId="com.android.systemui:id/lockPatternView").exists:
            print("  [Unlock] 偵測到圖形鎖，繪製 L 型...")
            self._draw_l_shape_pattern_lockscreen()

        elif self.d(resourceId="com.android.systemui:id/key1").exists or self.d(text="1").exists:
            print("  [Unlock] 偵測到 PIN 碼鍵盤，輸入 1234...")
            self._click_pin_buttons("1234")
            self.d.sleep(0.5)
            if self.d(resourceId="com.android.systemui:id/key_enter").exists:
                self.d(resourceId="com.android.systemui:id/key_enter").click()
            elif self.d(description="Enter").exists:
                self.d(description="Enter").click()

        elif self.d(className="android.widget.EditText").exists:
            print("  [Unlock] 偵測到密碼輸入框，輸入 Foxconn123...")
            self.d.send_keys("Foxconn123")
            self.d.sleep(0.5)
            self.d.press("enter")
        else:
            print("  [Info] 似乎已解鎖，或無密碼 (Swipe Only)。")

        self.d.sleep(1)
        print("  [System] 解鎖動作完成")

    def remove_screen_lock(self):
        """ 解除螢幕鎖定 (回到 None) """
        print("  [Security] 正在移除螢幕鎖定 ...")
        self.d.shell("am force-stop com.android.settings")
        self.d.sleep(1)
        self.d.shell("am start -W -a android.settings.SECURITY_SETTINGS -f 0x10008000")
        self.d.sleep(3)

        target_layout = self.d(className="android.widget.LinearLayout", clickable=True).child(text="Device unlock")

        found_unlock = False
        for _ in range(8):  # 最多嘗試滑動 8 次
            if target_layout.exists:
                found_unlock = True
                break

            print("  [Nav] 尚未發現 'Device unlock'...")
            # 獲取螢幕尺寸來計算滑動座標
            w, h = self.d.window_size()
            # 從螢幕 60% 高度滑到 40% 高度，steps=50 代表滑動速度極慢，減少慣性
            self.d.swipe(0.5 * w, 0.6 * h, 0.5 * w, 0.4 * h, steps=50)
            self.d.sleep(1)

        if found_unlock:
            print("  [Click] 已點擊 Device unlock 選項")
            target_layout.click()
        else:
            print("  [Fail] 找不到 'Device unlock' 選項")
            return

        self.d.sleep(1)

        found_lock = False
        for _ in range(5):
            if self.d(text="Screen lock").exists:
                found_lock = True
                break

            print("  [Nav] 尚未發現 'Screen lock'...")
            w, h = self.d.window_size()
            self.d.swipe(0.5 * w, 0.6 * h, 0.5 * w, 0.4 * h, steps=50)
            self.d.sleep(1)

        if found_lock:
            self.d(text="Screen lock").click()
        else:
            print("  [Fail] 找不到 'Screen lock' 選項")
            return

        self.d.sleep(1)

        is_in_selection_menu = False

        # 判斷依據 1: 看到 None 選項
        if self.d(text="None").exists or self.d(resourceId="com.android.settings:id/lock_none").exists:
            is_in_selection_menu = True
            print("  [Info] 偵測到 'None' 選項，代表無需驗證 (直接設定)")

        # 判斷依據 2: 看到 Swipe 且看到 PIN (代表已經進來列表了，只是 None 可能在上面被遮住)
        elif self.d(text="Swipe").exists and self.d(text="PIN").exists:
            is_in_selection_menu = True
            print("  [Info] 偵測到選單列表 (Swipe/PIN)，代表無需驗證")

        # =========================================================
        #  只有「不在」清單頁面時，才執行身份驗證
        # =========================================================
        if not is_in_selection_menu:
            print("  [Auth] 未在清單頁，判定需要身份驗證...")

            # 嘗試抓取標題文字 (這比盲猜準確)
            title_text = ""
            title_obj = self.d(resourceId="com.android.settings:id/suc_layout_title")
            if title_obj.exists:
                title_text = title_obj.get_text()
                print(f"  [Info] 驗證頁標題: {title_text}")

            # --- 分流處理 ---

            # 情況 A: PIN 碼 (標題有 PIN，或沒標題但有 PIN 字樣且不在選單模式)
            if "PIN" in title_text or (not title_text and self.d(textContains="PIN").exists):
                print("  [Action] 輸入 PIN 碼 (1234)...")
                self._input_text_lock("1234")
                self.d.press("enter")
                self.d.sleep(1)

            # 情況 B: 密碼 (Password)
            elif "Password" in title_text or self.d(className="android.widget.EditText").exists:
                # 如果標題沒寫 PIN 但有輸入框，或者是 Password，就輸密碼
                print("  [Action] 輸入密碼 (Foxconn123)...")
                self._input_text_lock("Foxconn123")
                self.d.press("enter")
                self.d.sleep(1)

            # 情況 C: 圖形鎖 (Pattern)
            elif "Pattern" in title_text or self.d(resourceId="com.android.settings:id/lockPattern").exists:
                print("  [Action] 繪製圖形鎖...")
                self._draw_l_shape_pattern()
                self.d.sleep(1)

            else:
                print("  [Warning] 無法識別鎖定類型，嘗試盲測尋找 None...")

        # 等待驗證後的轉場 (如果有驗證的話)
        self.d.sleep(1.5)

        # =========================================================
        # 🏁 設定為 None
        # =========================================================

        # 尋找 None
        none_option = self.d(text="None")
        if not none_option.exists:
            none_option = self.d(resourceId="com.android.settings:id/lock_none")

        # 如果因為螢幕小被擠到下面，嘗試滑動找 None
        if not none_option.exists:
            print("  [Nav] 尋找 None 選項中 (滑動)...")
            self.d(scrollable=True).scroll.to(text="None")

        if none_option.exists(timeout=3):
            print("  [Setting] 點擊 'None' 設定為無鎖定...")
            none_option.click()

            # 處理確認彈窗 (Remove device protection?)
            if self.d(textMatches="(?i)Delete|Remove|Yes|Clear").wait(timeout=3):
                print("  [Confirm] 確認移除...")
                if self.d(resourceId="android:id/button1").exists:
                    self.d(resourceId="android:id/button1").click()
                else:
                    self.d(textMatches="(?i)Delete|Remove|Yes|Clear").click()

            print("  [Success] 螢幕鎖定已移除 (None)")
        else:
            print("  [Fail] 依然找不到 None 選項！(可能卡在驗證頁或密碼錯誤)")
            return

        self.d.sleep(1)
        self.open_ctsv_from_recents()
        # self.d.press("home")

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
            self.d.swipe_points([p1, p4, p7, p8, p9], duration=0.2)

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
            w = right - left
            h = bottom - top

            # 定義點 (1->4->7->8->9)
            p1 = (left + w / 6, top + h / 6)
            p4 = (left + w / 6, top + h / 2)
            p7 = (left + w / 6, top + 5 * h / 6)
            p8 = (left + w / 2, top + 5 * h / 6)
            p9 = (left + 5 * w / 6, top + 5 * h / 6)

            self.d.swipe_points([p1, p4, p7, p8, p9], duration=0.2)


    def add_app_tile(self, app:str):
        """
        自動化 Step 2: 下拉狀態列 -> 編輯 -> 拖曳新增 'app'
        """
        print(f"  [QS] 正在嘗試將 '{app}' 加入快速設定面板...")

        # 1. 下拉狀態列 (兩次以展開完整 Quick Settings)
        self.d.open_quick_settings()
        self.d.sleep(1)

        # 2. 尋找並點擊「編輯 (鉛筆)」按鈕
        # 不同的 Android 版本/ROM ID 可能不同，這裡用通用的描述或 ID 嘗試
        edit_btn = self.d(description="Edit")  # 通用描述
        if not edit_btn.exists:
            edit_btn = self.d(resourceId="android:id/edit")  # 常見 ID

        if not edit_btn.exists:
            print("  [Fail] 找不到 Quick Settings 的編輯按鈕 (鉛筆圖示)")
            return False

        edit_btn.click()
        self.d.sleep(1.5)  # 等待編輯介面動畫

        # 3. 檢查 'app' 是否已經在「上方 (已啟用)」區域？
        # 如果已經在上面，就不需要再拖了
        # 我們用一個簡單的高度判斷：如果它在螢幕上半部，通常就是已啟用
        app_tile = self.d(text=app)

        if app_tile.exists:
            # 取得座標
            info = app_tile.info['bounds']
            cy = (info['top'] + info['bottom']) / 2
            h = self.d.window_size()[1]

            if cy < h * 0.5:
                print(f"  [Info] '{app}' 已經在啟用列表中，無需新增。")
                self.d.press("back")
                return True

        # 4. 在下方「可用列表」尋找 'app'
        # 如果第一頁沒看到，可能要往下滑
        if not app_tile.exists:
            print(f"  [Nav] 搜尋 '{app}' 圖示中...")
            self.d(scrollable=True).scroll.to(text=app)

        if not app_tile.exists:
            print(f"  [Fail] 找不到 '{app}' 圖示！請確認 apk 是否安裝成功？")
            self.d.press("back")
            return False

        # 5. 執行「拖曳」動作 (從下方拖到上方)
        print("  [Action] 執行拖曳動作...")

        # 目標位置：螢幕上方 1/3 處 (隨便找個已經存在的 Tile 位置丟過去)
        # 這裡我們直接設定一個絕對座標，通常是螢幕寬度的一半, 高度的 20%
        src_bounds = app_tile.info['bounds']
        sx = (src_bounds['left'] + src_bounds['right']) / 2
        sy = (src_bounds['top'] + src_bounds['bottom']) / 2

        # 2. 設定終點座標 (螢幕上方區域 30% 的位置，確保丟進 Active 區)
        w, h = self.d.window_size()
        dx, dy = w * 0.5, h * 0.1

        # 3. 開始執行分解動作
        try:
            # (A) 手指按下
            self.d.touch.down(sx, sy)

            # (B) 【關鍵】死按著不放，給予充足時間 (2.5秒)
            # 這是為了對抗 OEM 延遲，確保圖示「浮起來」
            # 就算機器很快，多按這 2 秒也不會導致失敗，但少按 0.1 秒就會失敗
            self.d.sleep(2.5)

            # (C) 移動 (模擬手指慢慢拖過去(dx, dy)
            # 透過迴圈手動發送 move 指令，取代會自動放開的 drag
            steps = 50
            for i in range(1, steps + 1):
                move_x = sx + (dx - sx) * (i / steps)
                move_y = sy + (dy - sy) * (i / steps)
                self.d.touch.move(move_x, move_y)
                self.d.sleep(0.04)

            self.d.sleep(3)

            # (E) 放開手指 帶入座標
            self.d.touch.up(dx, dy)

        except Exception as e:
            print(f"  [Fail] 拖曳過程發生例外: {e}")
            try:
                self.d.touch.up(dx, dy)
            except:
                pass  # 如果連 up 都失敗就不管了
            return False

        self.d.sleep(1)

        # 6. 返回並驗證
        self.d.press("back")
        self.d.sleep(1)

        if self.d(text=app).exists:
            print(f"  [Success] 成功加入 {app}！")
            return True
        else:
            print("  [Fail] 加入失敗，請檢查 UI 動作。")
            return False

    def settings_nav(self, *items, max_depth=5, per_item_scroll=10, settle=0.6):

        package_name = "com.android.settings"

        self.d.shell(f"am force-stop {package_name}")
        self.d.sleep(1)

        print(f"  [System] 正在啟動設定首頁...")
        self.d.shell("am start -W -a android.settings.SETTINGS -f 0x10008000")
        self.d.sleep(3)

        if not items:
            raise ValueError("settings_nav() needs at least 1 menu text")

        if len(items) > max_depth:
            raise ValueError(f"Too many levels: {len(items)} > max_depth={max_depth}")

        for level, text in enumerate(items, start=1):
            ok = self._scroll_find_and_click_text(
                text=text,
                max_scrolls=per_item_scroll,
                settle=settle,
                level=level
            )
            if not ok:
                print(f"  [Nav][Fail] Cannot find/click: '{text}' at level {level}")
                return False

        print("  [Nav][OK] Navigation finished")
        return True

    def settings_in_nav(self, *items, max_depth=5, per_item_scroll=10, settle=0.6):

        if len(items) > max_depth:
            raise ValueError(f"Too many levels: {len(items)} > max_depth={max_depth}")

        for level, text in enumerate(items, start=1):
            ok = self._scroll_find_and_click_text(
                text=text,
                max_scrolls=per_item_scroll,
                settle=settle,
                level=level
            )
            if not ok:
                print(f"  [Nav][Fail] Cannot find/click: '{text}' at level {level}")
                return False

        print("  [Nav][OK] Navigation finished")
        return True

    def _scroll_find_and_click_text(self, text, max_scrolls=10, settle=0.6, level=1):
        """
        在目前頁面尋找 text，找不到就滑；找到就點擊並驗證有轉場。
        """
        print(f"  [Nav][L{level}] Looking for '{text}'")

        # 0. 進場先看一眼 (萬一運氣好就在眼前)
        if self.d(textContains=text).exists:
            return self._click_and_confirm_transition(text=text, settle=settle, level=level)

        # 預設起始方向: forward (往下/往右)
        # True = Forward, False = Backward
        is_forward = True

        # 紀錄連續碰壁次數 (防止在不能滑的頁面無窮切換)
        stuck_count = 0

        for attempt in range(1, max_scrolls + 1):

            direction_str = "Down" if is_forward else "Up"

            scrolled = (
                self._scroll_forward_any_container()
                if is_forward
                else self._scroll_backward_any_container()
            )

            # 2. 判斷滑動結果 (核心邏輯)
            if not scrolled:
                # A. 沒滑動 = 撞牆了 (到底 or 到頂)
                stuck_count += 1
                print(f"  [Nav] Hit {direction_str} edge (Stuck: {stuck_count}), switching direction.")

                # 自動反轉方向
                is_forward = not is_forward

                # 如果連續兩次都滑不動 (代表頁面根本不能滑，或卡死)，就直接放棄
                if stuck_count >= 2:
                    print("  [Nav] 頁面無法捲動 (上下都卡住)，停止搜尋。")
                    break

                # 撞牆後這回合不算找過，直接進下一圈 (換方向滑)
                continue

            # B. 有滑動 = 重置卡住計數
            stuck_count = 0

            # 3. 滑動成功後，等待 UI 穩定並檢查
            self.d.sleep(0.25)

            if self.d(textContains=text).exists:
                return self._click_and_confirm_transition(text=text, settle=settle, level=level)

        print(f"  [Nav][Fail] Cannot find '{text}' after {max_scrolls} steps.")
        return False

    def _scroll_forward_any_container(self):
        """
        對可捲動容器做一次 forward 滑動；成功滑動就回 True。
        """
        before = self._ui_hash()

        for i in range(4):  # 通常 0~2 就夠，保險到 3
            s = self.d(scrollable=True, instance=i)
            if not s.exists:
                continue
            try:
                # [修正] 移除 moved = ，直接執行指令即可
                # u2 scroll.forward() 會回傳是否還能滑，但我們用 hash 判斷更準
                s.scroll.forward()

                self.d.sleep(0.15)
                if self._ui_hash() != before:
                    return True
            except Exception:
                pass

        # 沒有 scrollable 或都滑不動：用手勢滑一次當備案
        try:
            w, h = self.d.window_size()
            self.d.swipe(w * 0.5, h * 0.65, w * 0.5, h * 0.35, steps=40)
            self.d.sleep(0.15)
            return self._ui_hash() != before
        except Exception:
            return False

    def _scroll_backward_any_container(self):
        """
        對可捲動容器做一次 backward 滑動；成功滑動就回 True。
        """
        before = self._ui_hash()

        for i in range(6):
            s = self.d(scrollable=True, instance=i)
            if not s.exists:
                continue
            try:
                s.scroll.backward(steps=30)
                self.d.sleep(0.2)
                if self._ui_hash() != before:
                    return True
            except Exception:
                pass

        try:
            w, h = self.d.window_size()
            self.d.swipe(w * 0.5, h * 0.35, w * 0.5, h * 0.65, steps=35)
            self.d.sleep(0.2)
            return self._ui_hash() != before
        except Exception:
            return False


    def _click_and_confirm_transition(self, text, settle=0.6, level=1, allow_stay=False):
        """
        點擊 menu text 後，用「內容變化」確認真的有進下一頁。
        避免點了沒反應你還以為成功。
        """
        # 用 hierarchy hash 來判斷頁面有沒有變
        before = self._ui_hash()

        try:
            obj = self.d(textContains=text)
            if not obj.exists:
                print(f"  [Nav][L{level}][ClickFail] '{text}' not exists at click time")
                return False
            obj.click()
        except Exception as e:
            print(f"  [Nav][L{level}][ClickFail] '{text}' err={e}")
            return False

        self.d.sleep(settle)

        after = self._ui_hash()
        if after != before:
            print(f"  [Nav][L{level}] Click OK -> transitioned")
            return True

        self.d.sleep(1.0)
        after2 = self._ui_hash()
        if after2 != before:
            print(f"  [Nav][L{level}] Click OK -> delayed transition")
            return True

        print(f"  [Nav][L{level}][Warn] Clicked '{text}' but no transition detected")
        return allow_stay

    def _ui_hash(self):
        try:
            xml = self.d.dump_hierarchy(compressed=True)
            return hashlib.md5(xml.encode("utf-8")).hexdigest()
        except Exception:
            return f"fallback-{time.time()}"

    def switch_to_app_via_recents(self, target_name="CTS Verifier", timeout=10.0):
        print(f"  [Recents] 嘗試切換至目標: {target_name}")

        if not self._open_recents_safe():
            print("  [Recents] 無法開啟 Recents")
            return False

        self.d.sleep(1.0)
        start_time = time.time()

        while time.time() - start_time < timeout:

            # === 策略 1：Recents 常見是掛在 content-desc ===
            if self.d(descriptionContains=target_name).exists():
                node = self.d(descriptionContains=target_name)
                print(f"  [Recents] 以 description 命中: {target_name}")
                x, y = node.center()
                self.d.click(x, y)
                return True

            # === 策略 2：少數機型仍有 text（保留但正確判斷）===
            if self.d(textContains=target_name).exists():
                node = self.d(textContains=target_name)
                print(f"  [Recents] 以 text 命中: {target_name}")
                x, y = node.center()
                self.d.click(x, y)
                return True

            elif self.d.press("back"):
                print("  [Recents] 沒找到同名apk，點擊'back'，回到前一個app ")
                return True

            # 滑動 Recents
            w, h = self.d.window_size()
            self.d.swipe(w * 0.8, h * 0.5, w * 0.2, h * 0.5, steps=30)
            self.d.sleep(0.5)

        print(f"  [Recents] 超時，未找到 {target_name}")
        return False

    def _open_recents_safe(self):
        """
        安全地開啟最近工作清單，支援多種觸發方式。
        """
        # 方式 A: 標準鍵值點擊
        try:
            self.d.press("recent")
            return True
        except Exception:
            pass

        # 方式 B: 手勢滑動 (適應全螢幕手勢模式：從底部上滑並停留)
        try:
            w, h = self.d.window_size()
            self.d.swipe(w * 0.5, h * 0.99, w * 0.5, h * 0.6, steps=100)  # 慢滑模擬停留
            return True
        except Exception:
            return False

    def open_ctsv_from_recents(self):
        """
        [極速版] 從背景喚醒 CTS Verifier (Resume)。
        直接用 am start 指令把 Activity 拉到最上層，不走 Recents UI。
        """
        pkg = "com.android.cts.verifier"
        main_activity = "com.android.cts.verifier/.CtsVerifierActivity"

        print("  [Nav] Back to CTS Verifier ...")

        self.d.shell("cmd statusbar collapse")
        self.d.sleep(1)

        # 方法 1: 嘗試熱啟動 (Resume)
        # 只要不加 -f 0x10008000 (Clear Task)，am start 預設就是 "Bring to Front"
        # 這樣會保留您原本測試到一半的畫面，不會重置
        self.d.shell(f"am start -n {main_activity} -W")

        # 稍微等一下讓 App 彈出來
        # 通常指令下去 0.3 秒就好了，這邊給 1 秒緩衝
        if self.d(packageName=pkg).wait(timeout=2):
            print("  [App] 已切回 CTS Verifier。")
            self.d.sleep(2)
            return True

        # 方法 2: 如果熱啟動失效 (例如 App 被系統殺了)，才執行冷啟動 (Cold Start)
        print("  [App][Fallback] 喚醒失敗，執行強制重啟 ...")
        self.d.shell(f"sh -c 'am force-stop {pkg}; am start -n {main_activity} -W -f 0x10008000'")

        return self.d(packageName=pkg).wait(timeout=5)

    def _get_serial_from_file(self):
        """ 從檔案讀取 Setup 階段存下的序號 """
        if os.path.exists(self.serial_file):
            try:
                with open(self.serial_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if content:
                    return content
            except:
                pass

        print("  [Warning] 找不到序號暫存檔 (current_serial.txt)。")
        print("            如果是單獨執行腳本，請確認已先執行過 Setup。")
        # 這裡回傳空字串，u2 會嘗試連接第一台抓到的裝置
        return ""

    def _connect_device_with_retry(self, max_retries=3):
        """
        【核心功能】安全連線機制
        防止 http.client.RemoteDisconnected 錯誤
        """
        for attempt in range(1, max_retries + 1):
            try:
                # 嘗試連線
                d = u2.connect(self.serial)

                # 【重要】發送一個簡單指令確認連線是真的活著 (Ping)
                # 很多時候 connect 成功但 info 會失敗，所以要測
                _ = d.info

                if attempt > 1:
                    print(f"  [Init] 第 {attempt} 次嘗試連線成功！(Restored)")
                return d

            except Exception as e:
                print(f"  [Warning] 連線失敗 (嘗試 {attempt}/{max_retries}): {e}")

                if attempt < max_retries:
                    print("    -> 偵測到連線異常，正在嘗試修復環境...")
                    self._repair_environment()
                    # 給手機一點時間重啟 Agent
                    time.sleep(3)
                else:
                    print("  [Fail] 無法連接裝置，請檢查傳輸線或 ADB 狀態。")
                    # 這裡拋出異常，讓外面的程式知道真的沒救了
                    raise e

    def _repair_environment(self):
        """ 當連線失敗時，嘗試修復環境的手段 """
        print("    -> [Repair] 正在重啟手機端 Agent 與 ADB ...")
        try:
            # 強制停止手機上的 uiautomator 服務 (讓它下次重啟)
            subprocess.run(f"adb -s {self.serial} shell am force-stop com.github.uiautomator", shell=True)
            # 清除可能卡住的轉發規則
            subprocess.run(f"adb -s {self.serial} forward --remove-all", shell=True)
        except Exception as repair_error:
            print(f"    -> [Repair] 修復指令執行失敗: {repair_error}")

    def connect_fih_wifi(self):
        """
        自動連接公司網路 FIH-Free
        """
        wifi_ssid = "FIH-Free"
        print(f"  [Action] 準備連接 Wi-Fi: {wifi_ssid}")

        try:
            # 1. 確保 Wi-Fi 開關已開啟
            self.d.shell("svc wifi enable")
            self.d.sleep(1)

            # 2. 透過 ADB 強制連接指定 SSID (適用於無密碼或已儲存的網路)
            # cmd -w 代表等待執行完成
            connect_cmd = f"cmd wifi connect-network {wifi_ssid} open"
            self.d.shell(connect_cmd)

            # 3. 驗證連線狀態 (最多等待 10 秒)
            for i in range(20):
                # 透過 .output 取得指令的純文字結果
                wifi_info = self.d.shell("cmd wifi status").output

                # 判斷 SSID 是否存在於連線資訊中
                if wifi_ssid in wifi_info:
                    print(f"  [Pass] 已成功連接至 {wifi_ssid}")
                    return True

                self.d.sleep(1)

            print(f"  [Fail] 連接 {wifi_ssid} 超時")
            return False

        except Exception as e:
            print(f"  [Error] 連接 Wi-Fi 發生異常: {e}")
            return False

    def clear_all_notifications(self):
        """
        展開通知欄並清空所有通知。
        若通知過多，會自動往下滑動直到看見 'Clear all' 按鈕。
        """
        print("  [Action] 準備清空通知欄...")
        try:
            # 1. 透過 u2 指令展開系統通知欄
            self.d.open_notification()
            self.d.sleep(1.5)

            # 2. 如果畫面上還沒看到 "Clear all"，就驅動畫面往下滑找尋
            if not self.d(text="Clear all").exists:
                try:
                    # scrollable=True 代表尋找可滑動的區域，scroll.to 會一直滑動直到目標文字出現
                    for _ in range(5):
                        # 1. 先檢查畫面上是不是已經有 Clear all 了
                        if self.d(text="Clear all").exists:
                            break  # 如果有，就立刻跳出迴圈，停止滑動

                        # 2. 如果沒有，就強制畫面往下捲動一頁 (等同手指往上滑)
                        self.d(scrollable=True).scroll.forward()

                        # 3. 稍微等待畫面渲染，再進行下一次迴圈檢查
                        self.d.sleep(0.5)
                except Exception:
                    # 如果滑到底都沒有出現，代表可能被系統隱藏或真的沒有通知，略過報錯
                    pass

            # 3. 進行點擊判定
            if self.d(text="Clear all").exists:
                self.d(text="Clear all").click()
                print("  [Success] 已成功點擊 Clear all 按鈕，通知已清空")
                self.d.sleep(1)
            else:
                print("  [Skip] 找不到 Clear all 按鈕 (目前可能沒有可清除的通知)")
                # 按下返回鍵，把通知欄收起來，避免擋住後續測試
                self.d.press("back")

        except Exception as e:
            print(f"  [Error] 嘗試清空通知欄時發生異常: {e}")
            # 確保發生預期外錯誤時，也能盡量退出通知欄，不干擾主線程
            self.d.press("back")


    def click_final_pass(self):
        """ 當所有子測項都通過後，點擊主畫面左下角的 Pass 按鈕 """
        pass_btn = self.d(resourceId="com.android.cts.verifier:id/pass_button", enabled=True)
        fail_btn = self.d(resourceId="com.android.cts.verifier:id/fail_button")

        if pass_btn.wait(timeout=3):
            pass_btn.click()
            print("  [Pass] 該測項測試成功 ")
        else:
            fail_btn.click()
            print("  [Fail] 該測項測試出現異常 ")
