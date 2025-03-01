# 示例脚本：如何使用JQDataFetcher获取交易数据并通过ThsTrader执行交易
import sys
import os
import json
import time
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jqdata.__init__ import JQDataFetcher
from trader.__init__ import ThsTrader

def parse_trading_signal(trading_log):
    """解析交易日志，提取交易信号
    
    Args:
        trading_log (str): 聚宽平台获取的交易日志数据
        
    Returns:
        list: 交易信号列表，每个信号包含股票代码、价格、数量和操作类型
    """
    signals = []
    
    try:
        # 将日志字符串按行分割
        log_lines = trading_log.split('\n')
        
        for line in log_lines:
            if 'INFO  - order' in line:
                # 提取交易信息
                parts = line.split()
                trade_time = ' '.join(parts[0:2])
                stock_code = parts[5].split('=')[1]
                price = float(parts[-5].split(':')[1].rstrip(','))
                amount = int(parts[-4].split(':')[1].rstrip(','))
                action = 'buy' if 'side=long' in line else 'sell'
                
                signal = {
                    'stock_code': stock_code,
                    'price': price,
                    'amount': amount,
                    'action': action,
                    'time': trade_time
                }
                signals.append(signal)
    except Exception as e:
        print(f"解析交易信号失败: {str(e)}")
    
    return signals

def execute_trading(signals):
    """执行交易操作
    
    Args:
        signals (list): 交易信号列表
        
    Returns:
        list: 交易结果列表
    """
    results = []
    
    # 初始化同花顺交易执行器
    trader = ThsTrader()
    
    try:
        # 启动同花顺客户端
        if not trader.start():
            return [{"status": "error", "message": "启动同花顺客户端失败"}]
        
        # 执行每个交易信号
        for signal in signals:
            print(f"正在执行交易: {signal['action']} {signal['stock_code']} {signal['amount']}股 价格{signal['price']}")
            
            # 根据交易类型执行买入或卖出操作
            if signal['action'] == 'buy':
                result = trader.buy(signal['stock_code'], signal['price'], signal['amount'])
            else:
                result = trader.sell(signal['stock_code'], signal['price'], signal['amount'])
            
            # 添加交易结果
            result['stock_code'] = signal['stock_code']
            result['action'] = signal['action']
            result['time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            results.append(result)
            
            # 等待一段时间，避免操作过快
            time.sleep(2)
    
    except Exception as e:
        results.append({"status": "error", "message": f"交易执行过程中发生错误: {str(e)}"})
    
    finally:
        # 关闭同花顺客户端
        trader.close()
    
    return results

def main():
    # 初始化JQDataFetcher
    try:
        fetcher = JQDataFetcher()
        print("成功初始化JQDataFetcher，cookies已正确加载")
        
        # 获取交易日志数据
        backtest_id = "e0f45ee0101095f6e2f2350e87c47b93"  # 从cookies中提取的newBacktest值
        
        print(f"\n正在获取回测ID为 {backtest_id} 的交易日志...")
        trading_log = fetcher.get_trading_log(backtest_id)
        
        # 解析交易信号
        print("\n正在解析交易信号...")
        signals = parse_trading_signal(trading_log)
        print(f"解析到 {len(signals)} 个交易信号")
        
        if signals:
            # 执行交易
            print("\n开始执行交易操作...")
            results = execute_trading(signals)
            
            # 打印交易结果
            print("\n交易执行结果:")
            for result in results:
                status = "成功" if result.get("status") == "success" else "失败"
                print(f"{result.get('time')} {result.get('action')} {result.get('stock_code')} {status}: {result.get('message')}")
        else:
            print("\n未发现需要执行的交易信号")
        
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    main()