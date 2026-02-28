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
set "PYTHONPATH=%~dp0"

echo [系統] 目前工作路徑: %BASE_DIR%
echo [系統] 使用內置環境: %PY%

:: [清理] 測試開始前，先清空舊的 Log 檔
if exist "%LOG_FILE%" del /f /q "%LOG_FILE%"

:: ========================================================
:: [Step 0] 環境清理檢查與套件安裝
:: ========================================================
echo.
echo [Step 0] 正在檢查 Python 環境...

:: 檢查內置 Python 是否存在
if not exist "%PY%" (
    echo [Error] 找不到內置 Python 環境：%PY%
    pause
    exit /b
)

:: 安裝套件 (路徑已修正為 %BASE_DIR%)
"%PY%" -c "import requests" >nul 2>&1
if %errorlevel% neq 0 (
	if exist "%BASE_DIR%requirements.txt" (
		echo    %ARROW% 正在依照清單安裝必要套件...
		"%PY%" -m pip install -r "%BASE_DIR%requirements.txt" -q --disable-pip-version-check >> "%LOG_FILE%" 2>&1
	) else (
		echo    %ARROW% 找不到 requirements.txt，直接安裝預設套件...
		"%PY%" -m pip install requests beautifulsoup4 uiautomator2 -q --disable-pip-version-check >> "%LOG_FILE%" 2>&1
	)
)else (
    echo %ARROW% 套件環境檢查 OK。
)

:: ========================================================
:: [Step 1] 環境建置 (Clear & Setup)
:: ========================================================
echo.
echo [Step 1] 下載與環境建置...
echo %ARROW% Running Clear_Setup... >> "%LOG_FILE%"

"%PY%" "%BASE_DIR%Clear_Setup.py"
if %errorlevel% neq 0 (
    echo [Error] 環境建置失敗，請檢查 Log 或畫面訊息。
    pause
    exit /b
)
:: ========================================================
:: [Step 2] 執行測項 (螢幕 + Log 同步顯示)
:: ========================================================
echo.
echo [Step 2] 開始執行測試 ...

cd /d "%BASE_DIR%"

for %%i in (1_Clock 2_Device_Administration 3_Device_Controls 4_Display_Cutout 5_Features 6_Input 7_Install_Apps 8_Managed_Provisioning) do (
    echo.
	echo 正在執行: %%i...
	
    "%PY%" -u "%%i.py" >> "%LOG_FILE%" 2>&1
	
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
