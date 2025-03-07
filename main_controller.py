import os
import sys
import time
import logging
import threading
from queue import Queue
from open_ths_client import THSClient
from get_jq_data import fetch_jq_data
from extract_trade_signals import extract_trade_signals
from trade_executor import TradeExecutor

# 配置日志记录
log_file = 'logs/main_controller.log'
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

class MainController:
    def __init__(self):
        self.ths_client = None
        self.trade_executor = None
        self.signal_queue = Queue()
        self.running = False
        self.threads = []

    def start_ths_client(self):
        """启动同花顺客户端线程"""
        try:
            self.ths_client = THSClient(r"D:\同花顺\hexin.exe")
            if self.ths_client.open():
                logging.info("同花顺客户端已成功启动")
                time.sleep(3)  # 等待客户端初始化
                
                # 打开交易界面
                if self.ths_client.navigate_to_trading():
                    logging.info("交易界面已成功打开")
                    return True
                else:
                    logging.error("无法打开交易界面")
                    return False
            else:
                logging.error("无法启动同花顺客户端")
                return False
        except Exception as e:
            logging.error(f"启动同花顺客户端时出错: {e}")
            return False

    def jq_data_monitor(self):
        """聚宽数据监控线程"""
        while self.running:
            try:
                if fetch_jq_data():
                    logging.info("成功获取聚宽数据")
                time.sleep(300)  # 每5分钟检查一次
            except Exception as e:
                logging.error(f"获取聚宽数据时出错: {e}")
                time.sleep(60)  # 出错后等待1分钟再试

    def signal_processor(self):
        """信号处理线程"""
        while self.running:
            try:
                if not self.signal_queue.empty():
                    signals = self.signal_queue.get()
                    if signals:
                        self.trade_executor.execute_all_trades(signals)
                time.sleep(1)
            except Exception as e:
                logging.error(f"处理交易信号时出错: {e}")
                time.sleep(5)

    def start(self):
        """启动所有功能模块"""
        try:
            logging.info("正在启动交易系统...")
            
            # 启动同花顺客户端
            if not self.start_ths_client():
                logging.error("启动同花顺客户端失败，系统退出")
                return False

            self.running = True
            self.trade_executor = TradeExecutor()

            # 创建并启动线程
            threads = [
                threading.Thread(target=self.jq_data_monitor, name="JQ_Monitor"),
                threading.Thread(target=self.signal_processor, name="Signal_Processor")
            ]

            for thread in threads:
                thread.daemon = True
                thread.start()
                self.threads.append(thread)
                logging.info(f"线程 {thread.name} 已启动")

            logging.info("所有功能模块已启动完成")
            return True

        except Exception as e:
            logging.error(f"启动系统时出错: {e}")
            self.stop()
            return False

    def stop(self):
        """停止所有功能模块"""
        self.running = False
        for thread in self.threads:
            thread.join(timeout=5)
        logging.info("系统已停止")

def main():
    controller = MainController()
    if controller.start():
        try:
            # 保持主线程运行
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("接收到停止信号，正在关闭系统...")
            controller.stop()

if __name__ == '__main__':
    main()