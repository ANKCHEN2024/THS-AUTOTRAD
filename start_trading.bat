@echo off
chcp 65001

:: 创建日志目录
if not exist logs mkdir logs

:: 清屏并显示启动信息
cls
echo ====================================
echo      同花顺自动化交易系统启动
echo ====================================
echo.

:: 检查并激活虚拟环境
echo 正在检查虚拟环境...
if not exist "venv\Scripts\activate.bat" (
    echo 错误：未找到虚拟环境，请先运行 python -m venv venv 创建虚拟环境
    pause
    exit /b 1
)

:: 激活虚拟环境
call venv\Scripts\activate.bat

:: 检查依赖是否已安装
echo 正在检查依赖项...
pip list | findstr "requests"
if errorlevel 1 (
    echo 正在安装依赖项...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 错误：安装依赖项失败
        pause
        exit /b 1
    )
)

:: 启动同花顺客户端和交易系统
echo 正在启动同花顺客户端...
python open_ths_client.py

:: 启动数据获取和交易程序
echo 正在启动数据获取程序...
python get_jq_data.py

cls
echo ====================================
echo      系统启动完成！
echo ====================================
echo.
echo 所有程序已执行完成
echo.
pause