import requests
import json
import time
import datetime
import schedule
import os
from extract_trade_signals import extract_trade_signals
from trade_executor import TradeExecutor

def check_for_new_data(new_data):
    """检查是否有新数据"""
    try:
        with open('jq_log_data.json', 'r', encoding='utf-8') as f:
            old_data = json.load(f)
        return new_data['data']['logArr'] != old_data['data']['logArr']
    except FileNotFoundError:
        return True
    except json.JSONDecodeError:
        return True
    except Exception as e:
        print(f"检查新数据时出错: {e}")
        return False

def process_new_data():
    """处理新数据，提取交易信号并执行交易"""
    try:
        # 加载最新的日志数据
        with open('jq_log_data.json', 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        
        # 提取交易信号（已修改为只提取当天的交易信号）
        trade_signals = extract_trade_signals(log_data)
        
        if trade_signals:
            # 保存提取的交易信号
            with open('trade_signals.json', 'w', encoding='utf-8') as f:
                json.dump(trade_signals, f, ensure_ascii=False, indent=2)
            print(f"{datetime.datetime.now()} - 已提取{len(trade_signals)}个交易信号并保存")
            
            # 执行交易
            executor = TradeExecutor()
            executor.execute_all_trades(trade_signals)
        else:
            print(f"{datetime.datetime.now()} - 未发现新的交易信号")
    except Exception as e:
        print(f"{datetime.datetime.now()} - 处理新数据时出错: {e}")


def is_trading_time():
    """检查当前是否为交易时间"""
    now = datetime.datetime.now()
    # 如果是周末，不是交易时间
    if now.weekday() > 4:
        return False
    
    # 转换为时间对象进行比较
    current_time = now.time()
    morning_start = datetime.time(9, 30)
    morning_end = datetime.time(11, 30)
    afternoon_start = datetime.time(13, 0)
    afternoon_end = datetime.time(15, 0)
    
    # 判断是否在交易时间段内
    return ((current_time >= morning_start and current_time <= morning_end) or
            (current_time >= afternoon_start and current_time <= afternoon_end))

def is_special_time_point():
    """检查当前是否为需要特殊处理的时间点"""
    now = datetime.datetime.now()
    current_time = now.strftime('%H:%M')
    special_times = ['09:01', '09:26', '11:25', '14:50']
    return current_time in special_times

def fetch_jq_data():
    """获取聚宽数据"""
    if not is_trading_time():
        print(f"{datetime.datetime.now()} - 当前不是交易时间")
        return False
    
    # 检查是否为特殊时间点，如果是则延迟30秒
    if is_special_time_point():
        print(f"{datetime.datetime.now()} - 当前为关键时间点，延迟30秒后检查数据...")
        time.sleep(30)
    
    url = "https://www.joinquant.com/algorithm/live/log"
    params = {
        "backtestId": "c0d70622b43858da661ffa8261209e0b",
        "offset": "-1",
        "ajax": "1"
    }

    cookies = {
        "live_default_position_cols": "amount%2Cprice%2Cposition%2Cgain%2CgainPercent%2CdailyGainsPercent%2CpositionPersent",
        "token": "c8323c232db4ee2fada81dd80a37957b6ee0f177",
        "uid": "wKgyrWe+a6t8TgU9I7WaAg==",
        "getStrategy": "1",
        "from": "edit",
        "_xsrf": "2|ffc493a1|18404ccad881b1822f58a5db6c063ba1|1740763534",
        "newBacktest": "e0f45ee0101095f6e2f2350e87c47b93",
        "finishExtInfoce6985f6a07659d99d198c7c2a49a647": "1",
        "PHPSESSID": "idce09pgibnfspk1hrhmr9adk7"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }

    try:
        response = requests.get(url, params=params, cookies=cookies, headers=headers)
        print(f"{datetime.datetime.now()} - 状态码: {response.status_code}")
        
        # 尝试解析JSON响应
        try:
            data = response.json()
            
            # 检查是否有新数据
            has_new_data = check_for_new_data(data)
            
            # 将数据保存到文件
            with open("jq_log_data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"{datetime.datetime.now()} - 数据已更新并保存到 jq_log_data.json 文件")
            
            # 如果有新数据，触发交易信号提取和执行
            if has_new_data:
                print(f"{datetime.datetime.now()} - 检测到新数据，触发交易信号提取和执行")
                process_new_data()
                return True
            
            return False
        except json.JSONDecodeError:
            print(f"{datetime.datetime.now()} - 响应不是有效的JSON格式")
            return False
    except Exception as e:
        print(f"{datetime.datetime.now()} - 发生错误: {e}")
        return False

def main():
    # 设置定时任务，每5分钟执行一次
    schedule.every(5).minutes.do(fetch_jq_data)
    
    print("开始运行数据获取程序...")
    # 立即执行一次
    fetch_jq_data()
    
    # 持续运行定时任务
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()