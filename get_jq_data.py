import requests
import json
import time
import datetime
import schedule
import os
import logging
from extract_trade_signals import extract_trade_signals
from trade_executor import TradeExecutor

# 配置日志记录
log_file = 'logs/jq_data.log'
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
        logging.error(f"检查新数据时出错: {e}")
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
            logging.info(f"已提取{len(trade_signals)}个交易信号并保存")
            
            # 执行交易
            executor = TradeExecutor()
            executor.execute_all_trades(trade_signals)
        else:
            logging.info("未发现新的交易信号")
    except Exception as e:
        logging.error(f"处理新数据时出错: {e}")


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
        logging.info("当前不是交易时间")
        return False
    
    # 检查是否为特殊时间点，如果是则延迟30秒
    if is_special_time_point():
        logging.info("当前为关键时间点，延迟30秒后检查数据...")
        time.sleep(30)
    
    url = "https://www.joinquant.com/algorithm/live/log"
    params = {
        "backtestId": "c0d70622b43858da661ffa8261209e0b",
        "offset": "-1",
        "ajax": "1"
    }

    try:
        response = requests.get(url, params=params, cookies=cookies, headers=headers)
        logging.info(f"状态码: {response.status_code}")
        
        # 尝试解析JSON响应
        try:
            data = response.json()
            
            # 检查是否有新数据
            has_new_data = check_for_new_data(data)
            
            # 将数据保存到文件
            with open("jq_log_data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logging.info("数据已更新并保存到 jq_log_data.json 文件")
            
            # 如果有新数据，触发交易信号提取和执行
            if has_new_data:
                logging.info("检测到新数据，触发交易信号提取和执行")
                process_new_data()
                return True
            
            return False
        except json.JSONDecodeError:
            logging.error("响应不是有效的JSON格式")
            return False
    except Exception as e:
        logging.error(f"发生错误: {e}")
        return False

def main():
    # 设置定时任务，每5分钟执行一次
    schedule.every(5).minutes.do(fetch_jq_data)
    
    logging.info("开始运行数据获取程序...")
    # 立即执行一次
    fetch_jq_data()
    
    # 持续运行定时任务
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()