from auto import CtsVerifier
import argparse
import json

class Input(CtsVerifier):
    test_mapping = {"USI Version Test": "usi_version_test"}

    def _check_usi_hardware_support(self):
        """
        [Helper] 檢查 dumpsys input，判斷是否支援 USI
        """
        print("  [Check] 正在檢查系統硬體是否支援 USI 協議...")
        try:
            output = self.d.shell("dumpsys input").output

            # 判斷標準 1: 檢查是否有任何裝置的 UsiVersion 設定了數值 (非 <not set>)
            # 如果 output 裡有 "UsiVersion:" 但該行不包含 "<not set>"，代表有版本號
            lines = output.split('\n')
            for line in lines:
                if "UsiVersion:" in line:
                    if "<not set>" not in line:
                        print(f"    -> [Detected] 發現有效 USI 版本: {line.strip()}")
                        return True

            # 判斷標準 2: 檢查裝置名稱 (有些舊驅動可能沒報版本但名字有寫)
            if "USI" in output:
                print("    -> [Detected] 發現裝置名稱包含 'USI'")
                return True

            print("    -> [Result] 未發現 USI 支援特徵 (UsiVersion: <not set>)")
            return False

        except Exception as e:
            print(f"    [Error] 檢查硬體失敗: {e}")
            return False

    def usi_version_test(self):

        self.test_name = "USI Version Test"

        try:
            if not self.scroll_and_click(self.test_name):
                print(f"  [Fail] 未能進入{self.test_name}測項")
                self.go_back_to_list()
                return False

            if  self.d(textContains="Are you ready to proceed?").exists(timeout=3):
                self.d(resourceId = "com.android.cts.verifier:id/usi_yes_button").click()
                self.d.sleep(2)

            if self.d(textContains='Does the display "Built-in Screen" support styluses that use the USI protocol?').wait(timeout=3):

                is_supported = self._check_usi_hardware_support()

                if is_supported:
                    print("  [Check] 硬體支援 USI -> 點擊 Yes")
                    self.d(resourceId="com.android.cts.verifier:id/usi_yes_button").click()
                else:
                    print("  [Check] 硬體不支援 USI -> 點擊 No")
                    self.d(resourceId="com.android.cts.verifier:id/usi_no_button").click()

                self.d.sleep(2)

            if self.d(resourceId=self.btn_pass).exists(timeout=3):
                self.click_pass()
            else:
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--retry", type=str, help="JSON list of failed subtests")
    args = parser.parse_args()

    task = Input()
    try:
        if args.retry:
            fail_list = json.loads(args.retry)
            task.run_specific_tests(fail_list)
        else:
            task.usi_version_test()

    finally:
        try:
            task.d.stop_uiautomator()
        except:
            pass

