import os
import shutil
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import subprocess
import time
import zipfile
import glob

# 設定全域變數，確保清理和下載的路徑永遠一致
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 將 Downloads 資料夾建立在與腳本相同的目錄下
DOWNLOAD_DIR = os.path.join(BASE_DIR, "Downloads")


def clean_downloads_folder():
    """清空下載目錄，確保沒有舊版本的 APK 干擾。"""
    print(f"\n=== [Cleanup] 正在清空目錄: {DOWNLOAD_DIR} ===")

    if not os.path.exists(DOWNLOAD_DIR):
        print("  [Info] 目標目錄不存在，準備稍後建立。")
        return

    # 取得目錄下的所有項目
    for item in os.listdir(DOWNLOAD_DIR):
        item_path = os.path.join(DOWNLOAD_DIR, item)

        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)  # 刪除檔案
                print(f"  [Deleted File] {item}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # 刪除資料夾
                print(f"  [Deleted Dir]  {item}")
        except Exception as e:
            print(f"  [Error] 刪除失敗 {item}: {e}")

    print("\n=== 環境清理完畢 (All Clean) ===")


class EnvironmentSetup:
    def __init__(self):
        # 序號暫存檔路徑
        self.serial_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "current_serial.txt")

        # 下載路徑 (直接引用全域變數，避免打錯)
        self.save_dir = DOWNLOAD_DIR

        # 內網 CTS 下載點
        self.base_url = "http://10.57.42.97/RD/XTS/CTS/"

        # 目標檔案特徵
        self.target_keyword = "android-cts-verifier"
        self.target_ext = ".zip"

        # 1. 取得裝置序號 (讀檔或詢問)
        self.serial = self._get_or_select_serial()

    def _get_or_select_serial(self):
        """ 核心邏輯：有檔案就讀檔，沒檔案就選裝置並存檔 """

        # A. 嘗試讀取暫存檔
        if os.path.exists(self.serial_file):
            try:
                with open(self.serial_file, "r", encoding="utf-8") as f:
                    saved_serial = f.read().strip()
                if saved_serial:
                    # 這裡不印 log 保持畫面乾淨
                    return saved_serial
            except Exception:
                pass

                # B. 如果沒檔案 (或被刪除)，執行選擇邏輯
        selected_serial = self._select_device()

        # C. 選完立刻存檔
        try:
            with open(self.serial_file, "w", encoding="utf-8") as f:
                f.write(selected_serial)
        except Exception as e:
            print(f"  [Warning] 無法寫入序號暫存檔: {e}")

        return selected_serial

    def _select_device(self):
        """自動執行 adb devices 並讓使用者選擇"""
        try:
            result = subprocess.check_output(["adb", "devices"]).decode("utf-8")
            lines = result.strip().split('\n')[1:]
            devices = [line.split('\t')[0] for line in lines if line.strip() and '\tdevice' in line]

            if not devices:
                print("  [Error] 找不到任何已連線的 ADB 裝置，請檢查連線！")
                exit()

            if len(devices) == 1:
                print(f"  [Info] 偵測到唯一裝置: {devices[0]}")
                return devices[0]

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
        print(f"  [CMD] 執行: {command}")
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
        search_pattern = os.path.join(folder_path, "**", "CtsVerifier.apk")
        found_files = glob.glob(search_pattern, recursive=True)

        if found_files:
            return found_files[0]
        return None

    def _get_android_version(self):
        """透過 ADB 自動抓取設備的 Android 版本號"""
        print(f"  [Info] 正在透過 ADB 偵測 Android 版本...")
        try:
            # 加上 -s self.serial 確保對正確的設備下指令
            cmd = ["adb", "-s", self.serial, "shell", "getprop", "ro.build.version.release"]
            result = subprocess.check_output(cmd).decode("utf-8").strip()

            if result:
                print(f"  [Info] 成功偵測到 Android 版本: {result}")
                return result
            else:
                print("  [Error] ADB 回傳的 Android 版本為空字串。")
                return None
        except Exception as e:
            print(f"  [Error] 無法透過 ADB 獲取 Android 版本: {e}")
            return None

    def download_and_setup(self):
        print("\n=== CTSV 環境自動建置 (Zip Version) ===")
        # 1. 自動獲取 Android 版本
        os_version = self._get_android_version()
        if not os_version:
            print("  [Error] 無法確認 Android 版本，建置中斷。")
            return False

        # 組合目標 URL (保留完整的 os_version)
        target_url = urljoin(self.base_url, f"Android_{os_version}/")
        print(f"  [Connect] 正在連接內網: {target_url}")

        zip_save_path = None

        try:
            # === 1. 下載階段 ===
            response = requests.get(target_url, timeout=10)
            if response.status_code != 200:
                print(f"  [Error] 連線失敗 (Code: {response.status_code})")
                return False

            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a')

            available_zips = []
            for link in links:
                filename = link.get('href')
                # 檢查關鍵字與副檔名
                if filename and self.target_keyword in filename and filename.endswith(self.target_ext):
                    available_zips.append(filename)

            if not available_zips:
                print(f"  [Error] 在該目錄下找不到符合 '{self.target_keyword}' 的 Zip 檔案")
                return False

            # === 2. 選擇階段：多版本處理 ===
            selected_file = None
            if len(available_zips) > 1:
                print(f"\n  [Notice] 偵測到多個版本，請選擇欲下載的檔案:")
                for idx, name in enumerate(available_zips):
                    print(f"    [{idx}] {name}")

                try:
                    choice = int(input(f"  請輸入編號 (0-{len(available_zips) - 1}): ").strip())
                    selected_file = available_zips[choice]
                except (ValueError, IndexError):
                    print("  [Error] 輸入無效，取消下載")
                    return False
            else:
                selected_file = available_zips[0]

            # === 3. 下載階段 ===
            full_url = urljoin(target_url, selected_file)
            zip_save_path = os.path.join(self.save_dir, selected_file)

            print(f"\n  [Download] 準備下載: {selected_file}")
            with requests.get(full_url, stream=True) as r:
                r.raise_for_status()
                with open(zip_save_path, 'wb') as f:
                    # 使用 chunk 避免記憶體溢位
                    for chunk in r.iter_content(chunk_size=1024 * 1024):
                        f.write(chunk)

            print(f"  [Download] 下載完成: {zip_save_path}")


            if not zip_save_path:
                print(f"  [Error] 在該頁面找不到包含 '{self.target_keyword}' 的 zip 檔")
                return False

            # === 2. 解壓縮與搜尋階段 ===
            if not self.unzip_file(zip_save_path, self.save_dir):
                return False

            real_apk_path = self.find_apk_in_folder(self.save_dir)

            if not real_apk_path:
                print("  [Error] 解壓縮成功，但找不到 CtsVerifier.apk")
                return False

            print(f"  [Found] 找到 APK 路徑: {real_apk_path}")

            # === 3. 安裝與設定階段 ===
            print("\n  [Setup] 開始執行 ADB 安裝與權限設定...")
            self.run_cmd(f"adb -s {self.serial} shell settings put global hidden_api_policy 1")

            print(f"  [Install] 安裝主程式...")
            self.run_cmd(f"adb -s {self.serial} install -r -g \"{real_apk_path}\"")

            time.sleep(3)

            print("  [Config] 設定權限...")
            self.run_cmd(
                f"adb -s {self.serial} shell appops set com.android.cts.verifier android:read_device_identifiers allow")
            self.run_cmd(f"adb -s {self.serial} shell appops set com.android.cts.verifier MANAGE_EXTERNAL_STORAGE 0")
            self.run_cmd(f"adb -s {self.serial} shell am compat enable ALLOW_TEST_API_ACCESS com.android.cts.verifier")
            self.run_cmd(f"adb -s {self.serial} shell appops set com.android.cts.verifier TURN_SCREEN_ON 0")

            print("  [Launch] 正在啟動 CTS Verifier...")
            self.run_cmd(f"adb -s {self.serial} shell am start -n com.android.cts.verifier/.CtsVerifierActivity")

            return True

        except Exception as e:
            print(f"  [Error] 發生錯誤: {e}")
            return False


if __name__ == "__main__":
    # 1. 執行清理 (刪除舊 APK/Zip)
    clean_downloads_folder()

    # 2. 強制清除舊的序號記憶 (因為這是全新安裝)
    serial_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "current_serial.txt")
    if os.path.exists(serial_file_path):
        try:
            os.remove(serial_file_path)
            # print("  [Init] 已清除舊的序號暫存")
        except:
            pass

    # 3. 初始化並執行下載/安裝流程
    setup = EnvironmentSetup()
    setup.create_folder()

    if setup.download_and_setup():
        print("\n=== 環境建置成功！ ===")
    else:
        print("\n=== 環境建置失敗 ===")
        exit(1)