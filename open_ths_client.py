import os
import subprocess
import time
import sys
import psutil
import pyautogui
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ths_client.log', encoding='utf-8')
    ]
)

class THSClient:
    def __init__(self, ths_path=None):
        """
        初始化同花顺客户端
        
        参数:
            ths_path: 同花顺客户端安装路径，如果为None则使用默认路径
        """
        # 默认安装路径
        default_paths = [
            r"D:\同花顺\xiadan.exe",  # 网上股票交易应用程序路径
            r"D:\同花顺\hexin.exe"    # 同花顺客户端路径
        ]
        
        self.ths_path = ths_path
        
        # 如果未指定路径，尝试默认路径
        if self.ths_path is None:
            for path in default_paths:
                if os.path.exists(path):
                    self.ths_path = path
                    break
        
        if self.ths_path is None or not os.path.exists(self.ths_path):
            logging.error("未找到同花顺交易客户端，请指定正确的路径")
            raise FileNotFoundError("未找到同花顺交易客户端")
        
        logging.info(f"同花顺交易客户端路径: {self.ths_path}")
        
        self.process = None
    
    def is_running(self):
        """检查同花顺客户端是否正在运行"""
        if self.process is None:
            return False
        
        try:
            # 检查进程是否存在
            if self.process.poll() is None:
                return True
            return False
        except:
            return False
    
    def find_running_instance(self):
        """查找已经运行的同花顺实例"""
        # 根据文件路径的文件名来判断是哪个程序
        exe_name = os.path.basename(self.ths_path).lower()
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if exe_name in proc.info['name'].lower():
                    logging.info(f"找到正在运行的程序 {exe_name}，进程ID: {proc.info['pid']}")
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return None
    
    def open(self):
        """打开同花顺客户端"""
        # 检查是否已经有实例在运行
        existing_process = self.find_running_instance()
        if existing_process:
            logging.info("同花顺客户端已经在运行")
            return True
        
        try:
            logging.info("正在启动同花顺客户端...")
            # 使用shell=True确保程序能正常启动
            self.process = subprocess.Popen(self.ths_path, shell=True)
            time.sleep(3)  # 增加等待时间，确保程序完全启动
            
            if self.is_running():
                logging.info("同花顺客户端已成功启动")
                return True
            else:
                logging.error("同花顺客户端启动失败")
                return False
        except Exception as e:
            logging.error(f"启动同花顺客户端时出错: {e}")
            return False
    
    def close(self):
        """关闭同花顺客户端"""
        if not self.is_running():
            logging.info("同花顺客户端未运行")
            return True
        
        try:
            self.process.terminate()
            time.sleep(2)
            
            if self.is_running():
                self.process.kill()
                time.sleep(1)
            
            logging.info("同花顺客户端已关闭")
            return True
        except Exception as e:
            logging.error(f"关闭同花顺客户端时出错: {e}")
            return False
    
    def navigate_to_trading(self):
        """导航到交易界面"""
        try:
            # 等待界面加载
            time.sleep(3) # 增加等待时间
            
            # 由于图像识别可能不可靠，我们直接使用快捷键
            logging.info("尝试使用快捷键导航到交易界面")
            pyautogui.hotkey('alt', 't')
            time.sleep(2)
            return True
        except Exception as e:
            logging.error(f"导航到交易界面时出错: {e}")
            return False

def main():
    try:
        # 打开同花顺客户端
        client_hexin = THSClient(r"D:\同花顺\hexin.exe")
        if client_hexin.open():
            logging.info("同花顺客户端已成功启动")
        else:
            logging.error("无法启动同花顺客户端")
            return False  # 如果无法启动客户端，直接返回失败
        
        # 等待更长时间，让客户端有充分时间初始化
        time.sleep(3) # 增加等待时间
        
        # 尝试查找并点击同花顺主界面上的交易按钮
        try:
            # 激活同花顺窗口
            ths_window = None
            for window in pyautogui.getAllWindows():
                if "同花顺" in window.title and "网上股票交易" not in window.title:
                    ths_window = window
                    window.activate()
                    logging.info(f"已激活同花顺主窗口: {window.title}")
                    time.sleep(2)  # 增加等待时间
                    break
            
            if not ths_window:
                logging.error("未找到同花顺主窗口")
                return False
            
            # 先检查交易窗口是否已经打开
            trading_window = None
            for window in pyautogui.getAllWindows():
                if "网上股票交易系统5.0" in window.title:
                    trading_window = window
                    logging.info(f"找到交易窗口: {window.title}")
                    break
            
            # 如果交易窗口未打开，尝试打开
            if not trading_window:
                logging.info("交易窗口未打开，尝试使用F12快捷键打开")
                
                # 确保同花顺主窗口处于激活状态
                ths_window.activate()
                time.sleep(1)
                
                # 使用F12快捷键打开交易窗口
                pyautogui.press('f12')
                time.sleep(3) # 增加等待时间
                
                # 再次检查交易窗口是否已打开
                for window in pyautogui.getAllWindows():
                    if "网上股票交易系统5.0" in window.title:
                        trading_window = window
                        logging.info(f"交易窗口已打开: {window.title}")
                        break
                
                # 如果F12不起作用，尝试其他方法
                if not trading_window:
                    logging.info("F12快捷键未能打开交易窗口，尝试其他方法")
                    
                    # 尝试点击交易按钮（位置需要根据实际界面调整）
                    if ths_window:
                        # 点击主窗口中可能的交易按钮位置
                        button_x = ths_window.left + int(ths_window.width * 0.5)
                        button_y = ths_window.top + int(ths_window.height * 0.2)
                        pyautogui.click(button_x, button_y)
                        logging.info(f"尝试点击交易按钮位置: ({button_x}, {button_y})")
                        time.sleep(5)
                        
                        # 再次检查交易窗口
                        for window in pyautogui.getAllWindows():
                            if "网上股票交易系统5.0" in window.title:
                                trading_window = window
                                logging.info(f"交易窗口已打开: {window.title}")
                                break
            
            # 如果找到交易窗口，确保它在最前面
            if trading_window:
                # 激活交易窗口
                trading_window.activate()
                time.sleep(1)
                
                # 点击窗口中心以确保激活
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
        # 保持程序运行，不关闭软件
        logging.info("同花顺客户端已启动，程序将保持运行")
        
        # 删除了等待用户按回车键的输入提示
        
    except Exception as e:
        logging.error(f"运行过程中出错: {e}")

if __name__ == "__main__":
    main()