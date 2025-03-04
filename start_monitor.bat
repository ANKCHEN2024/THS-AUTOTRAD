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

:: Start THS client monitor
start "THS Client Monitor" /min cmd /k ""%~dp0venv\Scripts\python.exe" "%~dp0open_ths_client.py""

:: Wait for 2 seconds
timeout /t 2 /nobreak

:: Start JoinQuant data monitor
start "JoinQuant Data Monitor" /min cmd /k ""%~dp0venv\Scripts\python.exe" "%~dp0get_jq_data.py""

:: Wait for 2 seconds
timeout /t 2 /nobreak

:: Start trade signal extraction monitor
start "Trade Signal Monitor" /min cmd /k ""%~dp0venv\Scripts\python.exe" "%~dp0extract_trade_signals.py""

:: Wait for 2 seconds
timeout /t 2 /nobreak

:: Start trade execution monitor
start "Trade Execution Monitor" /min cmd /k ""%~dp0venv\Scripts\python.exe" "%~dp0trade_executor.py""

:: Keep window open
pause