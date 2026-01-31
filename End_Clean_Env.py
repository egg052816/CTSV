# 檔案名稱: End_Clear_env.py
import os
import shutil


def clean_downloads_folder():
    # 指定要清空的目錄 (必須與 Setup.py 的下載目錄一致)
    target_dir = r"D:\Python\CSTV\Downloads"

    print(f"\n=== [Cleanup] 正在清空目錄: {target_dir} ===")

    if not os.path.exists(target_dir):
        print("  [Info] 目標目錄不存在，無需清理。")
        return

    # 取得目錄下的所有項目 (不分副檔名，全部視為垃圾)
    for item in os.listdir(target_dir):
        item_path = os.path.join(target_dir, item)

        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)  # 刪除檔案
                print(f"  [Deleted File] {item}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # 刪除資料夾
                print(f"  [Deleted Dir]  {item}")
        except Exception as e:
            print(f"  [Error] 刪除失敗 {item}: {e}")

    print("=== 環境清理完畢 (All Clean) ===")


if __name__ == "__main__":
    clean_downloads_folder()