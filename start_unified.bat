@echo off

:: Set console code page to UTF-8
chcp 65001

:: Set console font to Consolas for better display
for /f "delims=" %%i in ('chcp ^| find "65001"') do set "output=%%i"
if not "%output%"=="" (
    reg add "HKEY_CURRENT_USER\Console" /v "FaceName" /t REG_SZ /d "Consolas" /f >nul 2>&1
)

:: Activate virtual environment
call "%~dp0venv\Scripts\activate.bat"

:: Start the unified controller
start "THS Trading System" cmd /k ""%~dp0venv\Scripts\python.exe" "%~dp0main_controller.py""

echo 同花顺自动化交易系统已启动，按任意键退出此窗口...
pause