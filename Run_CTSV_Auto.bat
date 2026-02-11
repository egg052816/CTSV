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
set "PY=python"
set "LOG_FILE=D:\Python\CTSV\execution_log.txt"

:: [清理] 測試開始前，先清空舊的 Log 檔
if exist "%LOG_FILE%" del /f /q "%LOG_FILE%"

:: ========================================================
:: [Step 0] 環境清理檢查與套件安裝
:: ========================================================
echo.
echo [Step 0] 正在檢查 Python 環境與必要套件...

:: 檢查 Python
%PY% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [Error] 您的電腦尚未安裝 Python！
    pause
    exit /b
)

:: 安裝套件 (保持安靜，只寫入 Log)
if exist "D:\Python\CTSV\requirements.txt" (
    echo   %ARROW% 正在依照清單安裝必要套件...
    %PY% -m pip install -r "D:\Python\CTSV\requirements.txt" -q --disable-pip-version-check >> "%LOG_FILE%" 2>&1
) else (
    echo   %ARROW% 找不到 requirements.txt，直接安裝預設套件...
    %PY% -m pip install requests beautifulsoup4 uiautomator2 -q --disable-pip-version-check >> "%LOG_FILE%" 2>&1
)

echo   %ARROW% 環境檢查完畢。

:: ========================================================
:: [Step 1] 環境建置 (Clear & Setup)
:: ========================================================
echo.
echo [Step 1] 下載與環境建置...
echo %ARROW% Running Clear_Setup... >> "%LOG_FILE%"

%PY% "D:\Python\CTSV\Clear_Setup.py"
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

:: --- 1_Clock ---
echo.
echo %ARROW% Running Clock Test...
echo ---------------------------------------- >> "%LOG_FILE%"
echo Running 1_Clock.py... >> "%LOG_FILE%"
%PY% -u "D:\Python\CTSV\1_Clock.py" 2>&1 | powershell -NoProfile -Command "$input | Tee-Object -FilePath '%LOG_FILE%' -Append"

:: --- 2_Device_Administration ---
echo.
echo %ARROW% Running Device Admin Test...
echo ---------------------------------------- >> "%LOG_FILE%"
echo Running 2_Device_Administration.py... >> "%LOG_FILE%"
%PY% -u "D:\Python\CTSV\2_Device_Administration.py" 2>&1 | powershell -NoProfile -Command "$input | Tee-Object -FilePath '%LOG_FILE%' -Append"

:: --- 3_Device_Controls ---
echo.
echo %ARROW% Running Device Controls Test...
echo ---------------------------------------- >> "%LOG_FILE%"
echo Running 3_Device_Controls.py... >> "%LOG_FILE%"
%PY% -u "D:\Python\CTSV\3_Device_Controls.py" 2>&1 | powershell -NoProfile -Command "$input | Tee-Object -FilePath '%LOG_FILE%' -Append"

:: --- 4_Display_Cutout ---
echo.
echo %ARROW% Running Display Cutout Test...
echo ---------------------------------------- >> "%LOG_FILE%"
echo Running 4_Display_Cutout.py... >> "%LOG_FILE%"
%PY% -u "D:\Python\CTSV\4_Display_Cutout.py" 2>&1 | powershell -NoProfile -Command "$input | Tee-Object -FilePath '%LOG_FILE%' -Append"

:: --- 5_Features ---
echo.
echo %ARROW% Running Features Test...
echo ---------------------------------------- >> "%LOG_FILE%"
echo Running 5_Features.py... >> "%LOG_FILE%"
%PY% -u "D:\Python\CTSV\5_Features.py" 2>&1 | powershell -NoProfile -Command "$input | Tee-Object -FilePath '%LOG_FILE%' -Append"

:: --- 6_Input ---
echo.
echo %ARROW% Running Input Test...
echo ---------------------------------------- >> "%LOG_FILE%"
echo Running 6_Input.py... >> "%LOG_FILE%"
%PY% -u "D:\Python\CTSV\6_Input.py" 2>&1 | powershell -NoProfile -Command "$input | Tee-Object -FilePath '%LOG_FILE%' -Append"

:: --- 7_Install_Apps ---
echo.
echo %ARROW% Running Install Apps Test...
echo ---------------------------------------- >> "%LOG_FILE%"
echo Running 7_Install_Apps.py... >> "%LOG_FILE%"
%PY% -u "D:\Python\CTSV\7_Install_Apps.py" 2>&1 | powershell -NoProfile -Command "$input | Tee-Object -FilePath '%LOG_FILE%' -Append"

:: --- 8_Managed_Provisioning ---
echo.
echo %ARROW% Running Install Apps Test...
echo ---------------------------------------- >> "%LOG_FILE%"
echo Running 8_Managed_Provisioning.py... >> "%LOG_FILE%"
%PY% -u "D:\Python\CTSV\8_Managed_Provisioning.py" 2>&1 | powershell -NoProfile -Command "$input | Tee-Object -FilePath '%LOG_FILE%' -Append"

:: ========================================================
:: [Step 3] 重跑 Fail 項目
:: ========================================================
echo.
echo [Step 3] 分析 Log 並執行 Retry...
echo ---------------------------------------- >> "%LOG_FILE%"
echo Running Retry.py... >> "%LOG_FILE%"
%PY% -u "D:\Python\CTSV\Retry.py" 2>&1 | powershell -NoProfile -Command "$input | Tee-Object -FilePath '%LOG_FILE%' -Append"

:: ========================================================
:: [Step 4] 最終清理與報告
:: ========================================================
echo.
echo [Step 4] 產生最終清理...
REM %PY% "D:\Python\CTSV\End_Clean_Env.py"

echo.
echo ========================================================
echo         測試結束
echo ========================================================
pause
endlocal
