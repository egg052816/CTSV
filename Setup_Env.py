# 檔案名稱: 1_Setup_Env.py
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import subprocess
import time
import zipfile  # [新增] 用來解壓縮
import glob  # [新增] 用來搜尋檔案


class EnvironmentSetup:
    def __init__(self):

        self.serial = self._select_device()
        self.base_url = "http://10.57.42.97/XTS/CTS/"
        self.save_dir = r"D:\Python\CSTV\Downloads"

        # [修改] 我們要找的是 zip 檔，且名稱要包含 verifier
        # 截圖顯示檔名類似: android-cts-verifier-14_r10-linux_x86-arm.zip
        self.target_keyword = "android-cts-verifier"
        self.target_ext = ".zip"

    def _select_device(self):
        """自動執行 adb devices 並讓使用者選擇"""
        try:
            # 執行 adb devices
            result = subprocess.check_output(["adb", "devices"]).decode("utf-8")
            lines = result.strip().split('\n')[1:]  # 跳過第一行 "List of devices attached"

            devices = [line.split('\t')[0] for line in lines if line.strip() and '\tdevice' in line]

            if not devices:
                print("  [Error] 找不到任何已連線的 ADB 裝置，請檢查連線！")
                exit()

            if len(devices) == 1:
                print(f"  [Info] 偵測到唯一裝置: {devices[0]}")
                return devices[0]

            # 多台裝置時顯示選單
            print("\n偵測到多台裝置，請選擇要測試的 Serial Number:")
            for i, sn in enumerate(devices):
                print(f"  [{i}] {sn}")

            choice = input("輸入編號 (預設 0): ").strip()
            idx = int(choice) if choice.isdigit() else 0

            if 0 <= idx < len(devices):
                selected = devices[idx]
                print(f"  [Info] 已選擇裝置: {selected}\n")
                return selected
            else:
                print("  [Warning] 編號錯誤，自動選擇第一台裝置。")
                return devices[0]

        except Exception as e:
            print(f"  [Error] 無法獲取裝置列表: {e}")
            exit()

    def create_folder(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            print(f"  [Init] 已建立資料夾: {self.save_dir}")

    def run_cmd(self, command):
        """ 執行系統 CMD 指令 """
        print(f"    [CMD] 執行: {command}")
        try:
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"    [Error] 指令執行失敗: {e}")

    def unzip_file(self, zip_path, extract_to):
        """ 解壓縮檔案 """
        print(f"  [Unzip] 正在解壓縮: {os.path.basename(zip_path)} ...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            print("  [Unzip] 解壓縮完成")
            return True
        except Exception as e:
            print(f"  [Error] 解壓縮失敗: {e}")
            return False

    def find_apk_in_folder(self, folder_path):
        """ 在資料夾中遞迴搜尋 CtsVerifier.apk """
        print("  [Search] 正在搜尋 CtsVerifier.apk ...")
        # 遞迴搜尋所有子目錄
        # glob 語法: D:\Python\CSTV\**\CtsVerifier.apk
        search_pattern = os.path.join(folder_path, "**", "CtsVerifier.apk")
        found_files = glob.glob(search_pattern, recursive=True)

        if found_files:
            return found_files[0]  # 回傳找到的第一個
        return None

    def download_and_setup(self):
        print("=== CTSV 環境自動建置 (Zip Version) ===")
        version_input = input("請輸入 Android 版本 (例如 14, 15): ").strip()

        target_url = urljoin(self.base_url, f"Android_{version_input}/")
        print(f"  [Connect] 正在連接內網: {target_url}")

        zip_save_path = None

        try:
            # === 1. 下載階段 (改抓 ZIP) ===
            response = requests.get(target_url, timeout=10)
            if response.status_code != 200:
                print(f"  [Error] 連線失敗 (Code: {response.status_code})")
                return False

            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a')

            for link in links:
                filename = link.get('href')

                # [邏輯] 檔名要有 "android-cts-verifier" 且結尾是 ".zip"
                # 這樣可以避開那個 11GB 的 android-cts-14...zip
                if filename and self.target_keyword in filename and filename.endswith(self.target_ext):
                    full_url = urljoin(target_url, filename)
                    zip_save_path = os.path.join(self.save_dir, filename)

                    print(f"  [Download] 發現壓縮包: {filename}")
                    print("             (檔案較大，請耐心等待下載...)")

                    # 下載
                    with requests.get(full_url, stream=True) as r:
                        r.raise_for_status()
                        with open(zip_save_path, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=1024 * 1024):  # 1MB chunk
                                f.write(chunk)

                    print(f"  [Download] 下載完成: {zip_save_path}")
                    break  # 找到了就停止搜尋

            if not zip_save_path:
                print(f"  [Error] 在該頁面找不到包含 '{self.target_keyword}' 的 zip 檔")
                return False

            # === 2. 解壓縮與搜尋階段 ===
            if not self.unzip_file(zip_save_path, self.save_dir):
                return False

            # 在解壓縮出來的資料夾中找 APK
            real_apk_path = self.find_apk_in_folder(self.save_dir)

            if not real_apk_path:
                print("  [Error] 解壓縮成功，但找不到 CtsVerifier.apk")
                return False

            print(f"  [Found] 找到 APK 路徑: {real_apk_path}")

            # === 3. 安裝與設定階段 ===
            print("\n  [Setup] 開始執行 ADB 安裝與權限設定...")

            self.run_cmd(f"adb -s {self.serial} shell settings put global hidden_api_policy 1")

            print(f"  [Install] 安裝主程式...")
            self.run_cmd(f"adb -s {self.serial} install -r -g \"{real_apk_path}\"")  # 加引號防止路徑有空白

            time.sleep(3)

            print("  [Config] 設定權限...")
            self.run_cmd(f"adb -s {self.serial} shell appops set com.android.cts.verifier android:read_device_identifiers allow")
            self.run_cmd(f"adb -s {self.serial} shell appops set com.android.cts.verifier MANAGE_EXTERNAL_STORAGE 0")
            self.run_cmd(f"adb -s {self.serial} shell am compat enable ALLOW_TEST_API_ACCESS com.android.cts.verifier")
            self.run_cmd(f"adb -s {self.serial} shell appops set com.android.cts.verifier TURN_SCREEN_ON 0")

            # === [新增] 啟動 App ===
            print("  [Launch] 正在啟動 CTS Verifier...")
            # am start -n (PackageName)/(ActivityName)
            self.run_cmd(f"adb -s {self.serial} shell am start -n com.android.cts.verifier/.CtsVerifierActivity")

            return True

        except Exception as e:
            print(f"  [Error] 發生錯誤: {e}")
            return False


if __name__ == "__main__":
    setup = EnvironmentSetup()
    setup.create_folder()
    if setup.download_and_setup():
        print("\n=== 環境建置成功！ ===")
    else:
        print("\n=== 環境建置失敗 ===")
        exit(1)