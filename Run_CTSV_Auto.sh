#!/bin/bash

# [設定] 強制 Python 輸出 UTF-8
export PYTHONIOENCODING=utf-8
clear

echo "========================================================"
echo "         CTS Verifier 自動化測試 (Auto-Flow)"
echo "========================================================"

# [變數] 定義
ARROW="->"
# 取得目前腳本所在的絕對路徑，等同於 batch 的 %~dp0
BASE_DIR=$(dirname "$(readlink -f "$0")")

# 注意：需依照您 Linux 環境的 Python 位置修改此變數
PY="python3" 

LOG_FILE="$BASE_DIR/execution_log.txt"
TEMP_LOG="$BASE_DIR/temp_run.log"
export PYTHONPATH="$BASE_DIR"

echo "[系統] 目前工作路徑: $BASE_DIR"
echo "[系統] 使用 Python 環境: $PY"

# [清理] 測試開始前，先清空舊的 Log 檔
[ -f "$LOG_FILE" ] && rm -f "$LOG_FILE"
[ -f "$TEMP_LOG" ] && rm -f "$TEMP_LOG"

# ========================================================
# [Step 0] 環境清理檢查與套件安裝
# ========================================================
echo ""
echo "[Step 0] 正在檢查 Python 環境..."

# 檢查 Python 是否存在
if ! command -v "$PY" &> /dev/null; then
    echo "[Error] 找不到 Python 環境：$PY"
    read -p "請按 Enter 鍵繼續..."
    exit 1
fi

# 安裝套件
if ! "$PY" -c "import requests" &> /dev/null; then
    if [ -f "$BASE_DIR/requirements.txt" ]; then
        echo "   $ARROW 正在依照清單安裝必要套件..."
        "$PY" -m pip install -r "$BASE_DIR/requirements.txt" -q --disable-pip-version-check >> "$LOG_FILE" 2>&1
    else
        echo "   $ARROW 找不到 requirements.txt，直接安裝預設套件..."
        "$PY" -m pip install requests beautifulsoup4 uiautomator2 -q --disable-pip-version-check >> "$LOG_FILE" 2>&1
    fi
else
    echo " $ARROW 套件環境檢查 OK。"
fi

# ========================================================
# [Step 1] 環境建置 (Clear & Setup)
# ========================================================
echo ""
echo "[Step 1] 下載與環境建置..."
echo "$ARROW Running Clear_Setup..." >> "$LOG_FILE"

"$PY" "$BASE_DIR/Clear_Setup.py"
if [ $? -ne 0 ]; then
    echo "[Error] 環境建置失敗，請檢查 Log 或畫面訊息。"
    read -p "請按 Enter 鍵繼續..."
    exit 1
fi

# ========================================================
# [Step 2] 執行測項 (螢幕 + Log 同步顯示)
# ========================================================
echo ""
echo "[Step 2] 開始執行測試 ..."

cd "$BASE_DIR" || exit 1

# 定義測項陣列
tests=(
    "1_Clock" "2_Device_Administration" "3_Device_Controls" 
    "4_Display_Cutout" "5_Features" "6_Input" "7_Install_Apps" 
    "11_Projection_Test" "12_Security" "13_Senors" "14_Streaming" "15_Tiles"
)

for i in "${tests[@]}"; do
    echo ""
    echo "正在執行: $i..."
    
    # 在 Linux 中使用 tee 指令即可達成 powershell Tee-Object 的效果
    "$PY" -u "$i.py" 2>&1 | tee -a "$TEMP_LOG"
    
    sleep 2
done

# ========================================================
# [Step 3] 重跑 Fail 項目
# ========================================================
echo ""
echo "[Step 3] 分析 Log 並執行 Retry..."

"$PY" -u "Retry.py" >> "$LOG_FILE" 2>&1

# ========================================================
# [Step 4] 最終清理與報告
# ========================================================
echo ""
echo "[系統] 測試全數跑完，正在將 Log 轉存至 $LOG_FILE..."

# 將暫存檔內容寫入正式 Log 檔
cat "$TEMP_LOG" > "$LOG_FILE"

# 刪除暫存檔
rm -f "$TEMP_LOG"

echo "[系統] Log 轉存完成。"

echo "[Step 4] 產生最終清理..."
# if [ -f "$BASE_DIR/End_Clean_Env.py" ]; then
#     "$PY" "$BASE_DIR/End_Clean_Env.py" >> "$LOG_FILE" 2>&1
# fi

echo ""
echo "========================================================"
echo "        測試結束"
echo "========================================================"
read -p "請按 Enter 鍵繼續..."
echo ""