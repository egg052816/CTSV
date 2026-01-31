@echo off
:: 設定編碼為 UTF-8，避免中文亂碼
chcp 65001
cls
echo ========================================================
echo          CTS Verifier 自動化測試 (Auto-Flow)
echo ========================================================

:: 設定 Python 執行指令
set PY=python

:: ========================================================
:: [Step 0] 環境檢查與套件安裝
:: ========================================================
echo.
echo [Step 0] 正在檢查 Python 環境與必要套件...

:: 1. 先檢查有沒有安裝 Python
%PY% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [Error] 您的電腦尚未安裝 Python，或是沒加入環境變數！
    echo 請先安裝 Python 3.x 並勾選 "Add to PATH"。
    pause
    exit /b
)

:: 2. 自動安裝 requirements.txt 裡面的套件
:: (為了避免語法錯誤，註解寫在 IF 外面)
:: 如果有 requirements.txt 就依照清單安裝，否則直接安裝常用套件
if exist D:\Python\CSTV\requirements.txt (
    echo   -> 正在依照清單安裝必要套件...
    %PY% -m pip install -r D:\Python\CSTV\requirements.txt -q --disable-pip-version-check
) else (
    echo   -> 找不到 requirements.txt，直接安裝預設套件...
    %PY% -m pip install requests beautifulsoup4 uiautomator2 -q --disable-pip-version-check
)

echo   -> 環境檢查完畢。

:: ========================================================
:: [Step 1] 環境建置
:: ========================================================
echo.
echo [Step 1] 下載與環境建置...
%PY% D:\Python\CSTV\Setup_Env.py

if %errorlevel% neq 0 (
    echo [Error] 環境建置失敗，測試中止。
    pause
    exit /b
)

:: ========================================================
:: [Step 2] 執行測項
:: ========================================================
echo.
echo [Step 2] 開始執行測試...

echo   -> Running Clock Test...
%PY% D:\Python\CSTV\1_Clock.py

echo   -> Running Device Admin Test...
%PY% D:\Python\CSTV\2_Device_Administration.py

:: ========================================================
:: [Step 3] 執行清理
:: ========================================================
echo.
echo [Step 3] 清理環境...
%PY% D:\Python\CSTV\End_Clean_Env.py

echo.
echo ========================================================
echo        測試結束
echo ========================================================
pause