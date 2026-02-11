from auto import CtsVerifier

class DisplayCutOut(CtsVerifier):

    def displaycutout_test(self):

        self.test_name = "DisplayCutout Test"

        try :
            if not self.scroll_and_click(self.test_name): return

            if self.d(text="Got it").exists(timeout=5):
                self.d(text="Got it").click()
            else:
                pass

            self.d.sleep(1)

            content = " This test is to make sure that the area inside the safe insets from the DisplayCutout should be"

            if self.d(textContains=content).exists():
                for i in range(16):
                    self.d(text=i).click()
                print(" [Info] 邊框 0~15 已點選完成")
            else:
                self.click_fail()

            if self.d(resourceId="com.android.cts.verifier:id/pass_button",enabled=True).exists():
                self.click_pass()

            else:
                self.click_fail()
                print(f" [Fail] {self.test_name} 結果不正確")

        except Exception as e:
            print(f"  [Crash] {self.test_name} 發生意外錯誤: {e}")

            self.d.screenshot(f"Crash_{self.test_name}.jpg")

            self.go_back_to_list()

if "__main__" == __name__:
    task = DisplayCutOut()
    task.displaycutout_test()






