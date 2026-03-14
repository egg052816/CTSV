from auto import CtsVerifier
import argparse
import json
import subprocess

class Sensors(CtsVerifier):
    test_mapping = {
        "6DoF Test": "six_dof_test",
        "Dynamic Sensor Discovery Test": "dynamic_sensor_discovery_test",
        "Off Body Sensor Tests": "off_body_sensor_tests"
    }

    def six_dof_test(self):

        self.test_name = "6DoF Test"

        try:
            if not self.scroll_and_click(self.test_name): return

            self.d.sleep(3)
            print(f"  [Check] 點擊 {self.test_name}，結果將自行判定")

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()



    def dynamic_sensor_discovery_test(self):

        self.test_name = "Dynamic Sensor Discovery Test"

        cmds = [
            "settings put global airplane_mode_on 1",
            "settings put system screen_brightness_mode 0",
            "settings put secure doze_enabled 0",
            "settings put secure doze_always_on 0",
            "settings put system accelerometer_rotation 0",
            "settings put global stay_on_while_plugged_in 0",
            "settings put system screen_off_timeout 15000",
        ]

        for cmd in cmds:
            full_cmd = f'adb -s {self.serial} shell {cmd}'
            subprocess.run(full_cmd, shell=True, capture_output=True)

        location_cmd = f'adb -s {self.serial} shell "settings put secure location_mode 0"'
        subprocess.run(location_cmd, shell=True, capture_output=True)
        if self.d(textContains="No location access").wait(10):
            print("  [Init] 已關 閉Adaptive Brightness、Ambient Display、Auto-rotate screen、Stay awake、Location 設定")
            self.d(className="android.widget.Button",text="Close").click()

        try:
            if not self.scroll_and_click(self.test_name): return

            self.d.sleep(1)
            self.d(resourceId="com.android.cts.verifier:id/next_button").click()
            self.d.sleep(0.5)

            if self.d(resourceId="com.android.cts.verifier:id/pass_button", enabled=True).wait(5):
                self.click_pass()
            else:
                print(f"  [Fail] {self.test_name} 測試失敗")
                self.click_fail()

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()


    def off_body_sensor_tests(self):

        self.test_name = "Off Body Sensor Tests"


        try:
            if not self.scroll_and_click(self.test_name): return

            self.d.sleep(1)
            self.d(resourceId="com.android.cts.verifier:id/next_button").click()
            self.d.sleep(1)

            print(f"  [Check] 點擊 {self.test_name}，結果將自行判定")


        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

        finally:
            restore_cmds = [
                "settings put global airplane_mode_on 0",  # 關閉飛行模式
                "settings put system screen_brightness_mode 1",  # 開啟自動亮度
                "settings put secure doze_enabled 1",  # 恢復環境顯示
                "settings put secure doze_always_on 1",
                "settings put system accelerometer_rotation 1",  # 開啟自動旋轉
                "settings put global stay_on_while_plugged_in 3",  # 恢復充電時保持喚醒 (AC/USB)
                "settings put system screen_off_timeout 1800000",  # 恢復螢幕逾時 (30分鐘)
                "settings put secure location_mode 3"  # 開啟定位 (High Accuracy)
            ]

            for cmd in restore_cmds:
                full_cmd = f'adb -s {self.serial} shell {cmd}'
                subprocess.run(full_cmd, shell=True, capture_output=True)


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

    task = Sensors()
    try:
        if args.retry:
            fail_list = json.loads(args.retry)
            task.run_specific_tests(fail_list)
        else:
            task.six_dof_test()
            task.dynamic_sensor_discovery_test()
            task.off_body_sensor_tests()
    finally:
        try:
            task.d.stop_uiautomator()

        except:
            pass







