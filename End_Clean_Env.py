import os
import shutil

# 設定全域變數，確保路徑一致
DOWNLOAD_DIR = r"D:\Python\CSTV\Downloads"
SERIAL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "current_serial.txt")
LOG_FILE = r"D:\Python\CSTV\execution_log.txt"


def clean_downloads_folder():
    """ 清空下載目錄 """
    print(f"\n=== [Cleanup] 正在清空目錄: {DOWNLOAD_DIR} ===")

    if not os.path.exists(DOWNLOAD_DIR):
        print("  [Info] 目標目錄不存在，無需清理。")
        return

    # 取得目錄下的所有項目
    for item in os.listdir(DOWNLOAD_DIR):
        item_path = os.path.join(DOWNLOAD_DIR, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
                print(f"  [Deleted File] {item}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"  [Deleted Dir]  {item}")
        except Exception as e:
            print(f"  [Error] 刪除失敗 {item}: {e}")


def remove_serial_cache():
    """ 刪除序號暫存檔 """
    if os.path.exists(SERIAL_FILE):
        try:
            os.remove(SERIAL_FILE)
            print(f"  [Clean] 已清除裝置序號暫存 ({os.path.basename(SERIAL_FILE)})")
        except Exception as e:
            print(f"  [Error] 清除序號失敗: {e}")
    else:
        print("  [Clean] 序號暫存檔已不存在。")


def archive_log():
    """ (選用) 將原本的 Log 改名備份，避免下次混淆 """
    if os.path.exists(LOG_FILE):
        # 例如改名為 execution_log_LAST_RUN.txt
        new_name = LOG_FILE.replace(".txt", "_LAST_RUN.txt")
        try:
            if os.path.exists(new_name):
                os.remove(new_name)
            os.rename(LOG_FILE, new_name)
            print(f"  [Log] 已將本次 Log 備份為: {os.path.basename(new_name)}")
        except:
            pass


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("          執行最終環境清理")
    print("=" * 50)

    # 1. 清理下載檔
    clean_downloads_folder()

    # 2. 清理序號 (這是最重要的，確保下次能選新裝置)
    remove_serial_cache()

    # 3. 處理 Log (看您需求，也可以不執行)
    # archive_log()

    print("\n=== 全部流程結束 (All Done) ===")