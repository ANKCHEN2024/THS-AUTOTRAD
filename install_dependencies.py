import subprocess
import sys
import os

def install_dependencies():
    """安装项目所需的依赖包"""
    print("开始安装依赖包...")
    
    # 检查是否在虚拟环境中
    in_venv = sys.prefix != sys.base_prefix
    if not in_venv:
        print("警告: 未检测到虚拟环境，建议在虚拟环境中安装依赖")
        response = input("是否继续安装? (y/n): ")
        if response.lower() != 'y':
            print("安装已取消")
            return
    
    # 要安装的依赖包列表
    dependencies = [
        "requests",
        "pandas",
        "psutil",
        "pyautogui",
        "pillow"  # pyautogui的图像处理依赖
    ]
    
    # 安装每个依赖包
    for package in dependencies:
        print(f"正在安装 {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"{package} 安装成功")
        except subprocess.CalledProcessError:
            print(f"安装 {package} 失败")
    
    print("\n所有依赖包安装完成")
    print("\n如果您需要使用同花顺自动化功能，请确保已安装以下依赖:")
    print("- psutil: 用于进程管理")
    print("- pyautogui: 用于屏幕操作和图像识别")
    print("- pillow: 用于图像处理")

if __name__ == "__main__":
    install_dependencies() 