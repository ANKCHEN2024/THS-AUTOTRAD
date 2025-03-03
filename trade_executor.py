import logging
import time
import os
import json
import sys

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extract_trade_signals import load_log_data, extract_trade_signals, group_trade_signals_by_date
import pyautogui

# 导入TradeWindowControl类
from trade_window_control import TradeWindowControl

# 导入open_ths_client模块
from open_ths_client import THSClient, main as open_ths_main

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('trade_executor.log', encoding='utf-8')
    ]
)

class TradeExecutor:
    def __init__(self):
        self.trade_control = TradeWindowControl()
        
    def ensure_trading_software_open(self):
        """确保同花顺交易软件已打开"""
        try:
            # 检查交易窗口是否已经打开
            for window in pyautogui.getAllWindows():
                if "网上股票交易" in window.title or "交易系统" in window.title:
                    logging.info(f"同花顺交易软件已打开: {window.title}")
                    return True
            
            # 如果没有找到交易窗口，直接调用open_ths_client.py的main函数
            logging.info("未找到交易窗口，尝试打开同花顺交易软件")
            open_ths_main()
            
            # 检查交易窗口是否已打开
            time.sleep(1)  # 等待交易窗口打开
            for window in pyautogui.getAllWindows():
                if "网上股票交易" in window.title or "交易系统" in window.title:
                    logging.info(f"成功打开同花顺交易软件: {window.title}")
                    return True
            
            logging.error("无法打开同花顺交易软件")
            return False
            
        except Exception as e:
            logging.error(f"确保交易软件打开时出错: {e}")
            return False
    
    def execute_single_trade(self, trade_signal):
        """执行单个交易信号"""
        try:
            # 确保同花顺交易软件已打开
            if not self.ensure_trading_software_open():
                logging.error("无法打开同花顺交易软件")
                return False
                
            # 确保交易窗口在最前面
            self.activate_trading_window()
            
            # 切换交易模式
            mode = 'buy' if trade_signal['交易类型'] == '买入' else 'sell'
            
            # 直接使用功能键切换到买入或卖出界面
            if mode == 'buy':
                # 使用F1键直接切换到买入界面
                pyautogui.press('f1')
                logging.info("使用F1键切换到买入界面")
            else:
                # 使用F2键直接切换到卖出界面
                pyautogui.press('f2')
                logging.info("使用F2键切换到卖出界面")
            
            time.sleep(1)  # 等待界面切换完成
            
            # 使用Alt+S快捷键直接定位到股票代码输入框
            pyautogui.hotkey('alt', 's')
            time.sleep(0.3)
            
            if mode == 'buy':
                # 买入操作 - 使用键盘导航
                # 清空并输入股票代码
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('delete')
                time.sleep(0.3)
                
                # 处理股票代码，确保格式正确
                stock_code = trade_signal['股票代码']
                if '.' in stock_code:
                    stock_code = stock_code.split('.')[0]
                pyautogui.typewrite(stock_code)
                logging.info(f"输入股票代码: {stock_code}")
                time.sleep(1)
                
                # 按Tab键移动到价格输入框
                pyautogui.press('tab')
                time.sleep(0.3)
                
                # 清空并输入价格
                pyautogui.hotkey('ctrl', 'a')
                for _ in range(5):  # 多次删除确保清空
                    pyautogui.press('backspace')
                time.sleep(0.3)
                
                try:
                    price_value = float(trade_signal['价格'])
                    price_str = f"{price_value:.2f}"
                    pyautogui.typewrite(price_str)
                    logging.info(f"输入价格: {price_str}")
                except Exception as e:
                    logging.error(f"价格输入出错: {e}")
                    return False
                
                time.sleep(1)
                # 按Tab键一次移动到数量输入框
                pyautogui.press('tab')
                time.sleep(0.3)
                
                # 清空并输入数量
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('delete')
                time.sleep(0.3)
                try:
                    amount = int(float(trade_signal['数量']))
                    amount_str = str(amount)
                    pyautogui.typewrite(amount_str)
                    logging.info(f"输入数量: {amount_str}")
                except Exception as e:
                    logging.error(f"数量输入出错: {e}")
                    return False
                
                time.sleep(1)
                
                # 按Tab键两次移动到买入按钮
                pyautogui.press('tab')
                time.sleep(0.3)
                
                # 按回车执行买入操作
                pyautogui.press('enter')
                logging.info("按下回车键执行买入操作")
                time.sleep(1)
            else:
                # 卖出模式 - 使用键盘导航
                # 清空并输入股票代码
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('delete')
                time.sleep(0.3)
                
                # 处理股票代码，确保格式正确
                stock_code = trade_signal['股票代码']
                if '.' in stock_code:
                    stock_code = stock_code.split('.')[0]
                pyautogui.typewrite(stock_code)
                logging.info(f"输入股票代码: {stock_code}")
                time.sleep(1)
                
                # 按Tab键移动到数量输入框
                pyautogui.press('tab')
                time.sleep(0.3)
                pyautogui.press('tab')
                time.sleep(0.3)
                
                # 清空并输入数量
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('delete')
                time.sleep(0.3)
                
                try:
                    amount = int(float(trade_signal['数量']))
                    amount_str = str(amount)
                    pyautogui.typewrite(amount_str)
                    logging.info(f"输入数量: {amount_str}")
                except Exception as e:
                    logging.error(f"数量输入出错: {e}")
                    return False
                
                time.sleep(1)
                
                # 按Tab键一次移动到卖出按钮
                pyautogui.press('tab')
                time.sleep(0.3)
                
                # 按回车执行卖出操作
                pyautogui.press('enter')
                logging.info("按下回车键执行卖出操作")
                time.sleep(1)
            
            # 处理可能出现的弹窗
            time.sleep(1)
            pyautogui.press('enter')  # 尝试关闭可能出现的弹窗
            
            logging.info(f"执行交易: {trade_signal['交易类型']} {stock_code} "
                        f"价格:{trade_signal.get('价格', '市价')} 数量:{trade_signal['数量']}")
            
            return True
            
        except Exception as e:
            logging.error(f"执行交易时出错: {e}")
            return False
            
    def get_trading_window(self):
        """获取交易窗口对象"""
        for window in pyautogui.getAllWindows():
            if "网上股票交易" in window.title or "交易系统" in window.title:
                return window
        return None
    def activate_trading_window(self):
        """激活交易窗口"""
        try:
            # 查找交易窗口
            found = False
            for window in pyautogui.getAllWindows():
                if "网上股票交易" in window.title or "交易系统" in window.title:
                    window.activate()
                    logging.info(f"已激活交易窗口: {window.title}")
                    found = True
                    time.sleep(1)
                    
                    # 点击窗口中心以确保激活
                    pyautogui.click(window.left + window.width // 2, 
                                   window.top + window.height // 2)
                    time.sleep(0.3)
                    break
            
            if not found:
                logging.warning("未找到交易窗口，尝试使用Alt+Tab切换")
                pyautogui.keyDown('alt')
                pyautogui.press('tab')
                pyautogui.keyUp('alt')
                time.sleep(1)
            
            return True
        except Exception as e:
            logging.error(f"激活交易窗口时出错: {e}")
            return False
    
    def execute_all_trades(self, trade_signals):
        """执行所有交易信号"""
        success_count = 0
        total_count = len(trade_signals)
        
        for signal in trade_signals:
            if self.execute_single_trade(signal):
                success_count += 1
            time.sleep(1)  # 交易之间的间隔
        
        logging.info(f"交易执行完成，成功: {success_count}/{total_count}")
        return success_count

def main():
    try:
        # 首先尝试查找已提取的交易信号文件
        current_dir = os.path.dirname(os.path.abspath(__file__))
        extracted_signals_file = os.path.join(current_dir, "trade_signals.json")
        
        trade_signals = []
        
        # 如果已提取的交易信号文件存在，直接加载
        if os.path.exists(extracted_signals_file):
            logging.info(f"从已提取的交易信号文件加载: {extracted_signals_file}")
            try:
                with open(extracted_signals_file, 'r', encoding='utf-8') as f:
                    trade_signals = json.load(f)
                logging.info(f"成功加载 {len(trade_signals)} 个交易信号")
            except Exception as e:
                logging.error(f"加载已提取的交易信号文件出错: {e}")
                trade_signals = []
        
        # 如果没有找到已提取的交易信号或加载失败，从原始日志提取
        if not trade_signals:
            logging.info("未找到已提取的交易信号，从原始日志提取")
            log_file = os.path.join(current_dir, "jq_log_data.json")
            
            if not os.path.exists(log_file):
                logging.error(f"原始日志文件不存在: {log_file}")
                print(f"错误：原始日志文件不存在: {log_file}")
                return
            
            # 加载并提取交易信号
            log_data = load_log_data(log_file)
            if not log_data:
                logging.error("加载原始日志数据失败")
                print("错误：加载原始日志数据失败")
                return
            
            trade_signals = extract_trade_signals(log_data)
            
            # 保存提取的交易信号，方便下次使用
            try:
                with open(extracted_signals_file, 'w', encoding='utf-8') as f:
                    json.dump(trade_signals, f, ensure_ascii=False, indent=2, default=str)
                logging.info(f"已将提取的交易信号保存到: {extracted_signals_file}")
            except Exception as e:
                logging.error(f"保存提取的交易信号时出错: {e}")
        
        if not trade_signals:
            logging.error("未找到交易信号")
            print("错误：未找到交易信号")
            return
        
        logging.info(f"找到 {len(trade_signals)} 个交易信号，准备执行")
        print(f"找到 {len(trade_signals)} 个交易信号，准备执行")
        
        # 执行交易
        executor = TradeExecutor()
        executor.execute_all_trades(trade_signals)
    
    except Exception as e:
        logging.error(f"执行过程中出错: {e}")
        print(f"错误：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()