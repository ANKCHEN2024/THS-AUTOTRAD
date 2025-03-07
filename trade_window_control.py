import pyautogui
import time
import logging
import os

# 配置日志
log_file = 'logs/trade_window.log'
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

class TradeWindowControl:
    def __init__(self):
        self.current_mode = None  # 当前模式：'buy' 或 'sell'
        
    def switch_trade_mode(self, mode):
        """
        切换交易模式（买入/卖出）
        
        参数:
            mode: 'buy' 或 'sell'
        """
        try:
            if mode not in ['buy', 'sell']:
                logging.error(f"无效的交易模式: {mode}")
                return False
                
            # 如果已经在目标模式，无需切换
            if self.current_mode == mode:
                logging.info(f"已经在{mode}模式，无需切换")
                return True
            
            # 根据模式选择快捷键
            if mode == 'buy':
                logging.info("切换到买入模式")
                pyautogui.press('f1')  # 买入快捷键
                self.current_mode = 'buy'
            else:
                logging.info("切换到卖出模式")
                pyautogui.press('f2')  # 卖出快捷键
                self.current_mode = 'sell'
            
            # 等待切换完成
            time.sleep(0.3)
            return True
            
        except Exception as e:
            logging.error(f"切换交易模式时出错: {e}")
            return False
    
    def verify_trade_mode(self):
        """
        验证当前交易模式（可以通过界面特征识别当前是买入还是卖出模式）
        """
        # 这里可以添加界面识别逻辑
        pass