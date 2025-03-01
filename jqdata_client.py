# 示例脚本：如何使用JQDataFetcher获取交易日志数据
import sys
import os
import json

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jqdata.__init__ import JQDataFetcher

def main():
    # 初始化JQDataFetcher
    try:
        fetcher = JQDataFetcher()
        print("成功初始化JQDataFetcher，cookies已正确加载")
        
        # 获取交易日志数据示例
        # 注意：您需要替换为您的实际回测ID
        backtest_id = "e0f45ee0101095f6e2f2350e87c47b93"  # 从cookies中提取的newBacktest值
        
        print(f"\n正在获取回测ID为 {backtest_id} 的交易日志...")
        trading_log = fetcher.get_trading_log(backtest_id)
        
        # 打印交易日志数据
        print("\n获取到的交易日志数据:")
        print(json.dumps(trading_log, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    main()