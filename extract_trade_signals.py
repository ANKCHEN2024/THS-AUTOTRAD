import json
import datetime
import logging
from collections import defaultdict

def load_log_data(file_path):
    """加载日志数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"加载日志数据失败: {e}")
        return None

def extract_trade_signals(log_data):
    """从日志数据中提取交易信号，只处理当天的交易信号"""
    if not log_data or 'data' not in log_data or 'logArr' not in log_data['data']:
        print("日志数据格式不正确")
        return []
    
    # 获取当前日期
    today = datetime.datetime.now().date()
    
    log_entries = log_data['data']['logArr']
    trade_signals = []
    
    for log in log_entries:
        try:
            # 解析日期和时间
            date_str = log.split(" - ")[0].strip()
            date_time = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            
            # 跳过非当天的交易信号
            if date_time.date() != today:
                continue
                
            # 检查是否包含委托买入信号
            if "订单已委托" in log and "action=open" in log:
                # 提取股票代码 - 只保留6位数字
                security_start = log.find("security=") + len("security=")
                security_end = log.find(".", security_start)
                security_full = log[security_start:security_end]
                security = ''.join(c for c in security_full if c.isdigit())[:6]
                
                # 提取价格
                price_start = log.find("_limit_price=") + len("_limit_price=")
                price_end = log.find(" ", price_start)
                price_str = log[price_start:price_end].strip()
                price = float(price_str)
                
                # 提取数量 - 从"调整为"后面提取
                amount_start = log.find("调整为") + len("调整为")
                amount_end = log.find(")", amount_start)
                amount_str = log[amount_start:amount_end].strip()
                amount = int(''.join(c for c in amount_str if c.isdigit()))
                
                # 记录交易信号
                trade_signal = {
                    "交易时间": date_time,
                    "交易类型": "买入",
                    "股票代码": security,
                    "价格": price,
                    "数量": amount
                }
                
                trade_signals.append(trade_signal)
                print(f"提取到买入信号: {trade_signal}")
            
            # 检查是否包含卖出信号
            elif "action=close" in log and "trade price:" in log:
                # 提取股票代码 - 只保留6位数字
                security_start = log.find("security=") + len("security=")
                security_end = log.find(".", security_start)
                security_full = log[security_start:security_end]
                security = ''.join(c for c in security_full if c.isdigit())[:6]
                
                # 提取价格 - 从trade price后面提取
                price_start = log.find("trade price:") + len("trade price:")
                price_end = log.find(",", price_start)
                price_str = log[price_start:price_end].strip()
                price = float(price_str)
                
                # 提取数量 - 从amount后面提取
                amount_start = log.find("amount:") + len("amount:")
                amount_end = log.find(",", amount_start)
                amount_str = log[amount_start:amount_end].strip()
                amount = int(''.join(c for c in amount_str if c.isdigit()))
                
                # 记录交易信号
                trade_signal = {
                    "交易时间": date_time,
                    "交易类型": "卖出",
                    "股票代码": security,
                    "价格": price,
                    "数量": amount
                }
                
                trade_signals.append(trade_signal)
                print(f"提取到卖出信号: {trade_signal}")
                
        except Exception as e:
            print(f"解析交易信号时出错: {e}, 日志内容: {log[:100]}...")
            continue
    
    # 按时间顺序排序
    trade_signals.sort(key=lambda x: x["交易时间"])
    
    return trade_signals

def group_trade_signals_by_date(trade_signals):
    """按日期对交易信号进行分组"""
    grouped_signals = defaultdict(list)
    
    for signal in trade_signals:
        date_key = signal["交易时间"].date()
        grouped_signals[date_key].append(signal)
    
    return grouped_signals

def print_trade_signals(trade_signals):
    """打印交易信号"""
    if not trade_signals:
        print("没有交易信号")
        return
    
    print("\n交易信号列表:")
    print("-" * 80)
    print(f"{'交易时间':<20} {'交易类型':<10} {'股票代码':<15} {'价格':<10} {'数量':<10}")
    print("-" * 80)
    
    for signal in trade_signals:
        print(f"{signal['交易时间'].strftime('%Y-%m-%d %H:%M:%S'):<20} {signal['交易类型']:<10} {signal['股票代码']:<15} {signal['价格']:<10.2f} {signal['数量']:<10}")

def print_grouped_signals(grouped_signals):
    """打印分组后的交易信号"""
    if not grouped_signals:
        print("没有分组交易信号")
        return
    
    for date, signals in sorted(grouped_signals.items()):
        print(f"\n日期: {date}")
        print("-" * 80)
        print(f"{'交易时间':<20} {'交易类型':<10} {'股票代码':<15} {'价格':<10} {'数量':<10}")
        print("-" * 80)
        
        for signal in signals:
            print(f"{signal['交易时间'].strftime('%Y-%m-%d %H:%M:%S'):<20} {signal['交易类型']:<10} {signal['股票代码']:<15} {signal['价格']:<10.2f} {signal['数量']:<10}")

def main():
    # 日志数据文件路径
    log_file = "jq_log_data.json"
    
    # 加载日志数据
    log_data = load_log_data(log_file)
    if not log_data:
        return
    
    # 提取交易信号
    trade_signals = extract_trade_signals(log_data)
    if not trade_signals:
        print("未找到交易信号")
        return
    
    # 按日期分组交易信号
    grouped_signals = group_trade_signals_by_date(trade_signals)
    
    # 打印分组后的交易信号
    print_grouped_signals(grouped_signals)

if __name__ == "__main__":
    main()