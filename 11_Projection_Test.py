from auto import CtsVerifier
import argparse
import json
import easyocr
from PIL import Image
import os

class ProjectionTest(CtsVerifier):
    test_mapping = {
        "Projection Offscreen Activity": "projection_offscreen_activity",
        "Projection Vidio Playback Test": "projection_vidio_playback_test",
        "Projection Widget Test": "projection_widget_test"
    }

    def projection_offscreen_activity(self):

        self.test_name = "Projection Offscreen Activity"

        try:
            if not self.scroll_and_click(self.test_name): return

            self.d.sleep(1)

            self.d.press("power")

            self.d.sleep(6)

            self.d.press("power")

            if self.d(resourceId="com.android.cts.verifier:id/pass_button", enabled=True).wait(3):
                self.click_pass()
            else:
                print(f"  [Fail] {self.test_name} 測試失敗")
                self.click_fail()

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()



    def projection_scrolling_list_test(self):

        self.test_name = "Projection Scrolling List Test"

        try:
            if not self.scroll_and_click(self.test_name): return

            width, height = self.d.window_size()

            # 設定滑動軌跡：從螢幕下方 80% 處滑到上方 20% 處 (模擬手指上滑)
            x = width * 0.5
            start_y = height * 0.8
            end_y = height * 0.2

            for i in range(1,5):
                self.d.swipe(x, start_y, x, end_y, duration=0.1)
                self.d.sleep(0.5)  # 等慣性停下來

            reader = easyocr.Reader(['en'])

            # 截圖並辨識
            result = reader.readtext(self.d.screenshot(format='opencv'))

            # 檢查結果
            found = False
            for (bbox, text, prob) in result:
                if "Item #50" in text:
                    found = True
                    break

            if found:
                self.click_pass()
            else:
                print(f"  [Fail] {self.test_name} 測試失敗")
                self.click_fail()

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()


    def projection_widget_test(self):
        self.test_name = "Projection Widget Test"
        screenshot_name = "projection_widget_test_screen.png"  # 統一定義檔名
        img = None

        try:
            # 1. 進入測試頁面
            if not self.scroll_and_click(self.test_name): return False

            print("  [Init]載入 OCR 模型中...")
            reader = easyocr.Reader(['en'], gpu=True)

            # 2. 截圖
            self.d.screenshot(screenshot_name)
            print("  [Init]正在進行 OCR 分析...")

            # 3. 讀取文字 (OCR)
            results = reader.readtext(screenshot_name)

            button_list = []

            # --- 迴圈 1: 找出所有 Button 的座標 ---
            for (bbox, text, prob) in results:
                if "Button" in text:
                    # bbox[0] = 左上, bbox[2] = 右下
                    top_left = bbox[0]
                    bottom_right = bbox[2]

                    center_x = int((top_left[0] + bottom_right[0]) / 2)
                    center_y = int((top_left[1] + bottom_right[1]) / 2)

                    button_list.append({
                        "center": (center_x, center_y),
                        "y": center_y
                    })

            # --- 以下邏輯必須移出 OCR 迴圈之外 ---

            # 4. 排序 (由上到下)
            button_list.sort(key=lambda x: x["y"])

            if len(button_list) == 0:
                print("  [Fail] OCR 沒看到任何 Button，請檢查畫面")
                return False

            # 5. 載入圖片來分析顏色 (使用剛剛截的那張圖)
            img = Image.open(screenshot_name)

            print(f"  [Check]找到 {len(button_list)} 個按鈕，開始分析狀態：")

            # --- 迴圈 2: 分析每個按鈕的顏色 ---
            for index, btn in enumerate(button_list):
                cx, cy = btn["center"]

                # 取得該點顏色
                r, g, b = img.getpixel((cx, cy))

                # 簡單的藍色判定 (視情況調整閾值)
                # 亮藍色通常 B 值很高，且 B > R
                if b > 200 and b > r + 30:
                    status = "【ACTIVE / 亮起】"
                else:
                    status = "Dim / 暗掉"

                print(f"  [Button] 按鈕 {index + 1} 座標({cx}, {cy}) | 顏色 R: {r} G:{g} B: {b} | 狀態: {status}")

            self.d(resourceId="com.android.cts.verifier:id/down_button").click();self.d.sleep(0.8)
            self.d(resourceId="com.android.cts.verifier:id/down_button").click();self.d.sleep(0.8)
            self.d(resourceId="com.android.cts.verifier:id/down_button").click();self.d.sleep(2)

            print("\n ========================================================================================== \n")

            self.d.screenshot(screenshot_name)
            img = Image.open(screenshot_name)
            active_button_index = -1

            for index, btn in enumerate(button_list):
                cx, cy = btn["center"]

                # 取得該點顏色
                r, g, b = img.getpixel((cx, cy))

                # 簡單的藍色判定 (視情況調整閾值)
                # 亮藍色通常 B 值很高，且 B > R
                if b > 200 and b > r + 30:
                    active_button_index = index
                    status = "【ACTIVE / 亮起】"
                else:
                    status = "Dim / 暗掉"

                print(f"  [Button] 按鈕 {index + 1} 座標({cx}, {cy}) | 顏色 R: {r} G:{g} B: {b} | 狀態: {status}")


            if active_button_index == 3:
                print("\n  [Pass] 確認 Down 功能正常,Button 4 成功亮起")

            else:
                # 失敗狀況分析
                if active_button_index == -1:
                    print("  [Fail] 沒有偵測到任何亮起的按鈕。")
                else:
                    print(f"  [Fail] 亮起的是 Button {active_button_index + 1} 顆，但預期應該是第 4 顆。")

                self.click_fail()
                return False

            self.d(resourceId="com.android.cts.verifier:id/up_button").click();self.d.sleep(0.8)
            self.d(resourceId="com.android.cts.verifier:id/up_button").click();self.d.sleep(2)

            print("\n ========================================================================================== \n")

            self.d.screenshot(screenshot_name)
            img = Image.open(screenshot_name)
            active_button_index = -1

            for index, btn in enumerate(button_list):
                cx, cy = btn["center"]

                # 取得該點顏色
                r, g, b = img.getpixel((cx, cy))

                # 簡單的藍色判定 (視情況調整閾值)
                # 亮藍色通常 B 值很高，且 B > R
                if b > 200 and b > r + 30:
                    active_button_index = index
                    status = "【ACTIVE / 亮起】"
                else:
                    status = "Dim / 暗掉"

                print(f"  [Button] 按鈕 {index + 1} 座標({cx}, {cy}) | 顏色 R: {r} G:{g} B: {b} | 狀態: {status}")

            if active_button_index == 1:
                print("\n  [Pass] 確認 Up 功能正常,Button 2 成功亮起")

            else:
                # 失敗狀況分析
                if active_button_index == -1:
                    print("  [Fail] 沒有偵測到任何亮起的按鈕。")
                else:
                    print(f"  [Fail] 亮起的是 Button {active_button_index + 1} 顆，但預期應該是第 2 顆。")

                self.click_fail()
                return False

            second_btn2_x, second_btn2_y = button_list[1]["center"]

            print(f"  [Check] 點擊Button 2,確認按鈕是否有暗掉")

            self.d.click(second_btn2_x, second_btn2_y)

            print("\n ========================================================================================== \n")

            self.d.screenshot(screenshot_name)
            img = Image.open(screenshot_name)
            active_button_index = -1

            for index, btn in enumerate(button_list):
                cx, cy = btn["center"]

                # 取得該點顏色
                r, g, b = img.getpixel((cx, cy))

                # 簡單的藍色判定 (視情況調整閾值)
                # 亮藍色通常 B 值很高，且 B > R
                if b > 200 and b > r + 30:
                    active_button_index = index
                    status = "【ACTIVE / 亮起】"
                else:
                    status = "Dim / 暗掉"

                print(f"  [Button] 按鈕 {index + 1} 座標({cx}, {cy}) | 顏色 R: {r} G:{g} B: {b} | 狀態: {status}")

            # 6. 驗證是否有按鈕亮起
            if active_button_index == -1:
                print(f"  [Pass] 檢測到 Button 2 已滅掉。")

                self.click_pass()
            else:
                print("  [Fail] 依舊偵測亮起的按鈕")
                self.click_fail()

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")
            self.d.screenshot(f"Crash_{self.test_name}.jpg")
            self.go_back_to_list()

        finally:
            if img is not None:
                try:
                    img.close()
                    print("  [Clean] 已釋放圖片物件資源")
                except:
                    pass

                # 2. 刪除該張暫存的照片
            if os.path.exists(screenshot_name):
                try:
                    os.remove(screenshot_name)
                    print(f"  [Clean] 已成功刪除暫存截圖: {screenshot_name}")
                except Exception as e:
                    print(f"  [Warn] 刪除截圖失敗: {e}")



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

    task = ProjectionTest()
    try:
        if args.retry:
            fail_list = json.loads(args.retry)
            task.run_specific_tests(fail_list)
        else:
            task.projection_offscreen_activity()
            task.projection_scrolling_list_test()
            task.projection_widget_test()
    finally:
        try:
            task.d.stop_uiautomator()
        except:
            pass







