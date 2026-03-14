from auto import CtsVerifier
import argparse
import json

class Streaming(CtsVerifier):
    class_name = "Streaming Video Quality Verifier"

    test_mapping = {
        "Streaming Video Quality Verifier": "streaming_video_quality_verifier",
    }

    def streaming_video_quality_verifier(self):

        if not self.scroll_and_click(self.class_name):
            print(f"  [Fail] 無法進入 {self.class_name}，停止測試。")
            self.go_back_to_list()
            return False

        if not self.connect_fih_wifi():
            print(f"  [Error] {self.class_name} 測試中止：Wi-Fi 連線失敗，無法播放影片。")
            self.click_fail()
            return False

        self.d.sleep(1)
        self.mpeg4_sp_video_aac_audio()
        self.h264_base_video_aac_audio()

    def mpeg4_sp_video_aac_audio(self):

        self.test_name = "MPEG4 SP Video, AAC Audio"

        try:
            if not self.enter_subtest(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                self.scroll_and_click(self.class_name)
                return False

            self.d.sleep(30)

            if self.d(resourceId="com.android.cts.verifier:id/pass_button", enabled=True).wait(5):
                self.click_pass()
                print(f"  [Success] {self.test_name} 播放完成")
            else:
                print(f"  [Fail] {self.test_name} 測試失敗")
                self.click_fail()

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()


    def h264_base_video_aac_audio(self):

        self.test_name = "H264 Base Video, AAC Audio"

        try:
            if not self.enter_subtest(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                self.scroll_and_click(self.class_name)
                return False

            self.d.sleep(30)

            if self.d(resourceId="com.android.cts.verifier:id/pass_button", enabled=True).wait(5):
                self.click_pass()
                print(f"  [Success] {self.test_name} 播放完成")
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

    task = Streaming()
    try:
        if args.retry:
            fail_list = json.loads(args.retry)
            task.run_specific_tests(fail_list)
        else:
            task.streaming_video_quality_verifier()

        task.click_final_pass()
    finally:
        try:
            task.d.stop_uiautomator()
        except:
            pass







