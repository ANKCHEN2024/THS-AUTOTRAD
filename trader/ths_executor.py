import os
import time
import pywinauto
from pathlib import Path
from typing import Dict, Optional

class ThsTrader:
    def __init__(self, xiadan_path: str = "D:\\同花顺\\xiadan.exe"):
        """初始化同花顺交易执行器

        Args:
            xiadan_path (str): 同花顺下单程序路径
        """
        self.xiadan_path = xiadan_path
        self.app = None
        self.main_window = None

    def start(self) -> bool:
        """启动同花顺客户端

        Returns:
            bool: 是否成功启动
        """
        try:
            if not os.path.exists(self.xiadan_path):
                raise FileNotFoundError(f"同花顺下单程序未找到：{self.xiadan_path}")

            # 启动客户端
            self.app = pywinauto.Application().start(self.xiadan_path)
            time.sleep(5)  # 等待程序启动

            # 连接到主窗口
            self.main_window = self.app.window(title_re="网上股票交易系统")
            self.main_window.wait('visible', timeout=10)
            return True

        except Exception as e:
            print(f"启动同花顺客户端失败: {str(e)}")
            return False

    def buy(self, stock_code: str, price: float, amount: int) -> Dict:
        """买入股票

        Args:
            stock_code (str): 股票代码
            price (float): 买入价格
            amount (int): 买入数量

        Returns:
            Dict: 交易结果
        """
        try:
            # 切换到买入界面
            self.main_window.type_keys("%1")  # Alt+1 打开买入界面
            time.sleep(1)

            # 输入交易参数
            self.main_window.type_keys(stock_code)
            time.sleep(0.5)
            self.main_window.type_keys("{TAB}")
            self.main_window.type_keys(str(price))
            time.sleep(0.5)
            self.main_window.type_keys("{TAB}")
            self.main_window.type_keys(str(amount))
            time.sleep(0.5)

            # 点击买入按钮
            self.main_window.type_keys("{ENTER}")
            time.sleep(1)

            # 处理确认对话框
            confirm_win = self.app.window(title="确认")
            if confirm_win.exists():
                confirm_win.type_keys("{ENTER}")

            return {"status": "success", "message": "买入委托已提交"}

        except Exception as e:
            return {"status": "error", "message": f"买入操作失败: {str(e)}"}

    def sell(self, stock_code: str, price: float, amount: int) -> Dict:
        """卖出股票

        Args:
            stock_code (str): 股票代码
            price (float): 卖出价格
            amount (int): 卖出数量

        Returns:
            Dict: 交易结果
        """
        try:
            # 切换到卖出界面
            self.main_window.type_keys("%2")  # Alt+2 打开卖出界面
            time.sleep(1)

            # 输入交易参数
            self.main_window.type_keys(stock_code)
            time.sleep(0.5)
            self.main_window.type_keys("{TAB}")
            self.main_window.type_keys(str(price))
            time.sleep(0.5)
            self.main_window.type_keys("{TAB}")
            self.main_window.type_keys(str(amount))
            time.sleep(0.5)

            # 点击卖出按钮
            self.main_window.type_keys("{ENTER}")
            time.sleep(1)

            # 处理确认对话框
            confirm_win = self.app.window(title="确认")
            if confirm_win.exists():
                confirm_win.type_keys("{ENTER}")

            return {"status": "success", "message": "卖出委托已提交"}

        except Exception as e:
            return {"status": "error", "message": f"卖出操作失败: {str(e)}"}

    def close(self):
        """关闭同花顺客户端"""
        if self.app:
            self.app.kill()
            self.app = None
            self.main_window = None