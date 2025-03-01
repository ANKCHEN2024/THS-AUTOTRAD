import os
import time
import pywinauto
from pathlib import Path
from typing import Dict, Optional

class ThsTrader:
    def __init__(self, xiadan_path: str = "D:\\同花顺\\xiadan.exe", hexin_path: str = "D:\\同花顺\\hexin.exe"):
        """初始化同花顺交易执行器

        Args:
            xiadan_path (str): 同花顺下单程序路径
            hexin_path (str): 同花顺主程序路径
        """
        self.xiadan_path = xiadan_path
        self.hexin_path = hexin_path
        self.app = None
        self.hexin_app = None
        self.main_window = None

    # 已移除set_account和get_verify_code方法，因为系统已设置自动登录

    def start(self) -> bool:
        """启动同花顺客户端

        Returns:
            bool: 是否成功启动
        """
        try:
            # 检查主程序和交易程序是否存在
            if not os.path.exists(self.hexin_path):
                print("错误：同花顺主程序未找到，请检查安装路径：" + self.hexin_path)
                return False
            if not os.path.exists(self.xiadan_path):
                print("错误：同花顺下单程序未找到，请检查安装路径：" + self.xiadan_path)
                return False

            # 尝试连接到已运行的程序
            try:
                self.hexin_app = pywinauto.Application().connect(path=self.hexin_path)
                print("已连接到运行中的同花顺主程序")
            except Exception:
                print("同花顺主程序未运行，正在启动...")
                try:
                    self.hexin_app = pywinauto.Application().start(self.hexin_path)
                    time.sleep(3)  # 等待主程序完全启动
                    print("同花顺主程序启动成功")
                except Exception as hexin_error:
                    print(f"启动主程序失败: {str(hexin_error)}")
                    return False

            # 尝试连接到已运行的交易客户端
            try:
                self.app = pywinauto.Application().connect(path=self.xiadan_path)
                print("已连接到运行中的交易客户端")
            except Exception:
                print("交易客户端未运行，正在启动...")
                try:
                    self.app = pywinauto.Application().start(self.xiadan_path)
                    time.sleep(3)  # 等待交易程序启动
                    print("交易客户端启动成功")
                except Exception as app_error:
                    print(f"启动交易客户端失败: {str(app_error)}")
                    if self.hexin_app:
                        self.hexin_app.kill()
                        self.hexin_app = None
                    return False

            # 等待一段时间，让程序自动登录（如果是新启动的话）
            time.sleep(3)
            print("等待自动登录完成...")
            print("正在等待主交易窗口...")

            # 尝试连接到主交易窗口，设置最大重试次数和超时时间
            max_retries = 10
            retry_interval = 2
            for i in range(max_retries):
                try:
                    # 查找主交易窗口，使用模糊匹配以适应不同版本的标题
                    windows = self.app.windows()
                    for w in windows:
                        if "网上股票交易系统" in w.window_text():
                            self.main_window = w
                            print("成功连接到主交易窗口")
                            return True
                    
                    if i < max_retries - 1:
                        print(f"未找到主交易窗口，{retry_interval}秒后重试...（{i + 1}/{max_retries}）")
                        time.sleep(retry_interval)
                    else:
                        print("无法找到主交易窗口，请确认交易客户端是否正常启动并登录")
                        return False
                        
                except Exception as e:
                    if i < max_retries - 1:
                        print(f"连接主交易窗口失败，{retry_interval}秒后重试...（{i + 1}/{max_retries}）")
                        time.sleep(retry_interval)
                    else:
                        print(f"连接主交易窗口失败: {str(e)}")
                        return False

            return False

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