import os
import subprocess
import time
import sys
import psutil
import pyautogui
import logging

# 配置日志记录
log_file = 'logs/ths_client.log'
os.makedirs('logs', exist_ok=True)

file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

class THSClient:
    def __init__(self, ths_path=None):
        """
        初始化同花顺客户端
        
        参数:
            ths_path: 同花顺客户端安装路径，如果为None则使用默认路径
        """
        # 定义默认的同花顺安装路径
        default_paths = [
            r"D:\同花顺\xiadan.exe",  # 网上股票交易应用程序路径
            r"D:\同花顺\hexin.exe"    # 同花顺客户端主程序路径
        ]
        
        self.ths_path = ths_path  # 存储用户指定的路径
        
        # 如果用户未指定路径，则尝试使用默认路径
        if self.ths_path is None:
            for path in default_paths:
                if os.path.exists(path):  # 检查路径是否存在
                    self.ths_path = path
                    break
        
        # 如果路径无效或文件不存在，则抛出异常
        if self.ths_path is None or not os.path.exists(self.ths_path):
            logging.error("未找到同花顺交易客户端，请指定正确的路径")
            raise FileNotFoundError("未找到同花顺交易客户端")
        
        logging.info(f"同花顺交易客户端路径: {self.ths_path}")
        
        self.process = None  # 初始化进程对象为None
    
    def is_running(self):
        """检查同花顺客户端是否正在运行"""
        if self.process is None:
            return False
        
        try:
            # 使用poll()方法检查进程状态，如果返回None表示进程仍在运行
            if self.process.poll() is None:
                return True
            return False
        except:
            return False
    
    def find_running_instance(self):
        """查找已经运行的同花顺实例"""
        # 获取可执行文件名（小写）用于进程匹配
        exe_name = os.path.basename(self.ths_path).lower()
        
        # 遍历系统中的所有进程
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # 检查进程名是否匹配同花顺程序
                if exe_name in proc.info['name'].lower():
                    logging.info(f"找到正在运行的程序 {exe_name}，进程ID: {proc.info['pid']}")
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass  # 忽略进程访问相关的异常
        return None
    
    def open(self):
        """打开同花顺客户端"""
        # 首先检查是否已有实例在运行
        existing_process = self.find_running_instance()
        if existing_process:
            logging.info("同花顺客户端已经在运行")
            return True
        
        try:
            logging.info("正在启动同花顺客户端...")
            # 使用subprocess.Popen启动程序，shell=True确保能正常启动Windows程序
            self.process = subprocess.Popen(self.ths_path, shell=True)
            time.sleep(5)  # 等待5秒，确保程序完全启动
            
            # 检查程序是否成功启动
            if self.is_running():
                logging.info("同花顺客户端已成功启动")
                return True
            else:
                logging.error("同花顺客户端启动失败")
                return False
        except Exception as e:
            logging.error(f"启动同花顺客户端时出错: {e}")
            return False

    def navigate_to_trading(self):
        """打开交易界面"""
        try:
            # 等待界面完全加载
            time.sleep(3)
            
            # 使用F12快捷键打开交易界面，避免使用不可靠的图像识别
            logging.info("尝试使用F12快捷键打开交易界面")
            pyautogui.press('f12')
            time.sleep(5)  # 等待界面切换完成
            return True
        except Exception as e:
            logging.error(f"打开交易界面时出错: {e}")
            return False

def main():
    """主函数：启动同花顺客户端并打开交易界面"""
    try:
        # 创建并启动同花顺客户端实例
        client_hexin = THSClient(r"D:\同花顺\hexin.exe")
        if client_hexin.open():
            logging.info("同花顺客户端已成功启动")
        else:
            logging.error("无法启动同花顺客户端")
            return False
        
        # 等待客户端初始化
        time.sleep(3)
        
        # 自动打开交易窗口的处理流程
        try:
            # 查找并激活同花顺主窗口
            ths_window = None
            for window in pyautogui.getAllWindows():
                if "同花顺" in window.title and "网上股票交易" not in window.title:
                    ths_window = window
                    window.activate()  # 激活窗口
                    logging.info(f"已激活同花顺主窗口: {window.title}")
                    time.sleep(2)
                    break
            
            if not ths_window:
                logging.error("未找到同花顺主窗口")
                return False
            
            # 检查交易窗口是否已经打开
            trading_window = None
            for window in pyautogui.getAllWindows():
                if "网上股票交易系统5.0" in window.title:
                    trading_window = window
                    logging.info(f"找到交易窗口: {window.title}")
                    break
            
            # 如果交易窗口未打开，尝试多种方式打开它
            if not trading_window:
                logging.info("交易窗口未打开，尝试使用F12快捷键打开")
                
                # 确保主窗口处于激活状态
                ths_window.activate()
                time.sleep(1)
                
                # 尝试使用F12快捷键打开交易窗口
                pyautogui.press('f12')
                time.sleep(5)
                
                # 检查F12快捷键是否成功打开交易窗口
                for window in pyautogui.getAllWindows():
                    if "网上股票交易系统5.0" in window.title:
                        trading_window = window
                        logging.info(f"交易窗口已打开: {window.title}")
                        break
                
                # 如果F12快捷键失败，尝试点击交易按钮
                if not trading_window:
                    logging.info("F12快捷键未能打开交易窗口，尝试其他方法")
                    
                    if ths_window:
                        # 计算并点击主窗口中交易按钮的估计位置
                        button_x = ths_window.left + int(ths_window.width * 0.5)
                        button_y = ths_window.top + int(ths_window.height * 0.2)
                        pyautogui.click(button_x, button_y)
                        logging.info(f"尝试点击交易按钮位置: ({button_x}, {button_y})")
                        time.sleep(5)
                        
                        # 再次检查交易窗口是否打开
                        for window in pyautogui.getAllWindows():
                            if "网上股票交易系统5.0" in window.title:
                                trading_window = window
                                logging.info(f"交易窗口已打开: {window.title}")
                                break
            
            # 如果成功找到交易窗口，确保它在最前面
            if trading_window:
                # 激活交易窗口
                trading_window.activate()
                time.sleep(1)
                
                # 点击窗口中心以确保窗口真正激活
                window_center_x = trading_window.left + trading_window.width // 2
                window_center_y = trading_window.top + trading_window.height // 2
                pyautogui.click(window_center_x, window_center_y)
                
                logging.info(f"已将交易窗口 '{trading_window.title}' 置于最前面")
                return True
            else:
                logging.error("未能打开交易窗口")
                return False
                
        except Exception as e:
            logging.error(f"通过同花顺客户端启动交易功能时出错: {e}")
            return False
        
    except Exception as e:
        logging.error(f"运行过程中出错: {e}")
        return False

if __name__ == "__main__":
    main()  # 当脚本直接运行时，执行main函数