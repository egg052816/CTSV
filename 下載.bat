@echo off
setlocal

:: [設定] 編碼為 UTF-8，並強制 Python 輸出 UTF-8
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cls

echo ========================================================
echo          CTS Verifier 自動化測試 (Auto-Flow)
echo ========================================================

:: [變數] 定義
set "ARROW= "
set "BASE_DIR=%~dp0"
set "PY=%BASE_DIR%python_311\python.exe"
set "LOG_FILE=%BASE_DIR%execution_log.txt"
set "TEMP_LOG=%BASE_DIR%temp_run.log"
set "PYTHONPATH=%~dp0"

REM echo [系統] 目前工作路徑: %BASE_DIR%
REM echo [系統] 使用內置環境: %PY%

REM :: [清理] 測試開始前，先清空舊的 Log 檔
REM if exist "%LOG_FILE%" del /f /q "%LOG_FILE%"

REM :: ========================================================
REM :: [Step 0] 環境清理檢查與套件安裝
REM :: ========================================================
REM echo.
REM echo [Step 0] 正在檢查 Python 環境...

REM :: 檢查內置 Python 是否存在
REM if not exist "%PY%" (
    REM echo [Error] 找不到內置 Python 環境：%PY%
    REM pause
    REM exit /b
REM )

REM :: 安裝套件 (路徑已修正為 %BASE_DIR%)
REM "%PY%" -m pip install -r "%BASE_DIR%requirements.txt" -q --disable-pip-version-check
REM if %errorlevel% neq 0 (
	REM if exist "%BASE_DIR%requirements.txt" (
		REM echo    %ARROW% 正在依照清單安裝必要套件...
		REM "%PY%" -m pip install -r "%BASE_DIR%requirements.txt" -q --disable-pip-version-check >> "%LOG_FILE%" 2>&1
	REM ) else (
		REM echo    %ARROW% 找不到 requirements.txt，直接安裝預設套件...
		REM "%PY%" -m pip install requests beautifulsoup4 uiautomator2 -q --disable-pip-version-check >> "%LOG_FILE%" 2>&1
	REM )
REM )else (
    REM echo %ARROW% 套件環境檢查 OK。
REM )

REM :: ========================================================
REM :: [Step 1] 環境建置 (Clear & Setup)
REM :: ========================================================
REM echo.
REM echo [Step 1] 下載與環境建置...
REM echo %ARROW% Running Clear_Setup... >> "%LOG_FILE%"

REM "%PY%" "%BASE_DIR%Clear_Setup.py"
REM if %errorlevel% neq 0 (
    REM echo [Error] 環境建置失敗，請檢查 Log 或畫面訊息。
    REM pause
    REM exit /b
REM )
:: ========================================================
:: [Step 2] 執行測項 (螢幕 + Log 同步顯示)
:: ========================================================
echo.
echo [Step 2] 開始執行測試 ...

cd /d "%BASE_DIR%"

for %%i in (9) do (
    echo.
    echo 正在執行: %%i...
    
    "%PY%" -u "%%i.py" 2>&1 | powershell -NoProfile -Command "$input | Tee-Object -FilePath '%TEMP_LOG%' -Append"
    
    timeout /t 2 >nul
)
:: ========================================================
:: [Step 3] 重跑 Fail 項目
:: ========================================================
echo.
echo [Step 3] 分析 Log 並執行 Retry...

"%PY%" -u "Retry.py" >> "%LOG_FILE%" 2>&1

:: ========================================================
:: [Step 4] 最終清理與報告
:: ========================================================
echo.

echo [系統] 測試全數跑完，正在將 Log 轉存至 %LOG_FILE%...

:: 將暫存檔內容寫入正式 Log 檔
type "%TEMP_LOG%" > "%LOG_FILE%"

:: 刪除暫存檔 (可選)
del "%TEMP_LOG%"

echo [系統] Log 轉存完成。


echo [Step 4] 產生最終清理...
REM if exist "%BASE_DIR%End_Clean_Env.py" (
    REM "%PY%" "%BASE_DIR%End_Clean_Env.py" >> "%LOG_FILE%" 2>&1
REM )

echo.
echo ========================================================
echo         測試結束
echo ========================================================
pause
endlocal
