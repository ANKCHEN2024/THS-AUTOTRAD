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
        # 解析JSON格式的日志数据
        log_data = json.loads(trading_log)
        log_lines = log_data['data']['logArr']
        
        for line in log_lines:
            # 检查是否包含买入信号
            if 'INFO  - 买入' in line and '，金额:' in line:
                try:
                    # 提取交易时间
                    parts = line.split()
                    trade_time = ' '.join(parts[0:2])
                    
                    # 提取股票代码 - 格式通常为: "买入 股票代码"
                    stock_info = line.split('买入')[1].split('，')[0].strip()
                    stock_code = stock_info.split()[0]  # 获取第一个部分作为股票代码
                    
                    # 提取金额部分
                    amount_str = line.split('，金额:')[1].strip()
                    amount_value = float(amount_str)
                    
                    # 在后续日志中查找该股票的订单信息
                    order_info = None
                    for order_line in log_lines:
                        if stock_code in order_line and '开仓数量必须是100的整数倍，调整为' in order_line:
                            # 提取调整后的数量
                            amount = int(order_line.split('调整为')[1].split(':')[0].strip())
                            order_info = order_line
                            break
                    
                    # 如果找到了订单信息，则添加到信号列表中
                    if order_info:
                        # 从后续日志中查找价格信息
                        price = 0
                        for price_line in log_lines:
                            if stock_code in price_line and '当前价格加上滑点后' in price_line:
                                price_str = price_line.split('当前价格加上滑点后')[1].split()[0].strip()
                                price = float(price_str)
                                break
                        
                        signal = {
                            'stock_code': stock_code,
                            'price': price,
                            'amount': amount,
                            'action': 'buy',  # 转换为英文，与execute_trading函数匹配
                            'time': trade_time
                        }
                        signals.append(signal)
                except Exception as e:
                    print(f"解析单条交易信号失败: {str(e)}")
                    continue
            
            # 检查是否包含卖出信号 (如果有的话)
            elif 'INFO  - 卖出' in line:
                # 卖出信号的解析逻辑，根据实际日志格式调整
                pass
                
    except Exception as e:
        print(f"解析交易信号失败: {str(e)}")
    
    return signals

def main():
    # 初始化同花顺交易执行器
    try:
        trader = ThsTrader()
        print("\n正在启动同花顺客户端...")
        
        # 已设置自动登录，不需要手动设置账号和密码
        
        # 启动同花顺客户端
        if not trader.start():
            print("启动同花顺客户端失败，请检查软件是否正确安装并且可以正常运行")
            return
            
        print("同花顺客户端启动成功")
        
        # 初始化JQDataFetcher
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
            results = []
            
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
            
            # 打印交易结果
            print("\n交易执行结果:")
            for result in results:
                status = "成功" if result.get("status") == "success" else "失败"
                print(f"{result.get('time')} {result.get('action')} {result.get('stock_code')} {status}: {result.get('message')}")
        else:
            print("\n未发现需要执行的交易信号")
        
    except Exception as e:
        print(f"错误: {str(e)}")
    finally:
        # 不再自动关闭同花顺客户端，由用户自行管理
        pass

if __name__ == "__main__":
    main()