import requests
import json
import time
import datetime
import schedule
import os
import logging
import re
from extract_trade_signals import extract_trade_signals
from trade_executor import TradeExecutor
from config_manager import get_credentials

# 配置日志记录
log_file = 'logs/jq_data.log'
os.makedirs('logs', exist_ok=True)

# 移除所有已存在的处理器
logger = logging.getLogger()
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def check_for_new_data(new_data):
    """检查是否有新数据"""
    try:
        with open('data/jq_log_data.json', 'r', encoding='utf-8') as f:
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
        with open('data/jq_log_data.json', 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        
        # 提取交易信号（已修改为只提取当天的交易信号）
        trade_signals = extract_trade_signals(log_data)
        
        if trade_signals:
            # 保存提取的交易信号
            with open('data/trade_signals.json', 'w', encoding='utf-8') as f:
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

def update_cookies():
    """自动更新cookies"""
    try:
        logging.info("尝试自动更新cookies...")
        
        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # 创建会话并设置重定向处理
        session = requests.Session()
        session.max_redirects = 5
        
        # 访问聚宽登录页面获取初始cookies和CSRF令牌
        login_url = "https://www.joinquant.com/user/login/index?type=login"
        response = session.get(login_url, headers=headers)
        
        if response.status_code != 200:
            logging.error(f"访问登录页面失败，状态码: {response.status_code}")
            return None, None
            
        # 尝试从页面内容中提取token
        window_token = None
        try:
            # 查找页面中的token
            token_match = re.search(r'window\.tokenData={name:"token",value:"([^"]+)"', response.text)
            if token_match:
                window_token = token_match.group(1)
                logging.info(f"成功从页面提取token")
            else:
                logging.error("未能从页面提取token")
                return None, None
        except Exception as e:
            logging.warning(f"从页面提取token时出错: {e}")
            return None, None
        
        # 从配置文件获取加密的用户名和密码
        username, password = get_credentials()
        if not username or not password:
            logging.error("无法获取登录凭据，请确保已正确配置账号信息")
            return None, None
            
        # 执行登录操作
        login_data = {
            'username': username,
            'password': password,
            'remember_me': 'true',
            'return_url': '/',
            'type': 'login'
        }
        
        # 不再需要CSRF令牌，直接使用window_token
        # 聚宽网站现在使用window_token进行身份验证
        
        # 更新请求头
        headers['Referer'] = login_url
        headers['Origin'] = 'https://www.joinquant.com'
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        headers['X-Requested-With'] = 'XMLHttpRequest'
        
        # 发送登录请求
        login_api = "https://www.joinquant.com/user/login/index"
        login_data['token'] = window_token  # 添加从页面获取的token
        login_response = session.post(login_api, data=login_data, headers=headers, allow_redirects=True)
        
        if login_response.status_code != 200:
            logging.error(f"登录请求失败，状态码: {response.status_code}")
            return None, None
            
        # 检查登录响应是否包含成功信息
        try:
            login_result = login_response.json()
            if login_result.get('code') != 200:
                logging.error(f"登录失败: {login_result.get('msg', '未知错误')}")
                logging.error(f"详细错误信息: {json.dumps(login_result, ensure_ascii=False, indent=2)}")
                logging.debug(f"登录请求详情 - URL: {login_api}, 用户名: {username}, 响应内容: {login_response.text}")
                return None, None
            logging.info("登录API返回成功状态")
        except Exception as e:
            logging.warning(f"解析登录响应时出错: {e}，继续尝试获取cookies")
            logging.debug(f"登录响应内容: {login_response.text}")
        
        # 获取cookies
        cookies_dict = session.cookies.get_dict()
        
        if not cookies_dict:
            logging.error("无法获取新的cookies")
            return None, None
        
        # 检查是否包含_xsrf字段
        if '_xsrf' not in cookies_dict:
            logging.warning("获取的新cookies中缺少_xsrf字段，尝试访问多个页面获取完整cookies")
            
            # 尝试访问多个页面，以获取完整的cookies
            try:
                # 访问用户主页
                home_url = "https://www.joinquant.com/user/home/index"
                session.get(home_url, headers=headers)
                
                # 访问算法页面
                algo_url = "https://www.joinquant.com/algorithm"
                session.get(algo_url, headers=headers)
                
                # 访问社区页面
                community_url = "https://www.joinquant.com/community"
                session.get(community_url, headers=headers)
                
                # 更新cookies
                cookies_dict = session.cookies.get_dict()
                logging.info("已尝试通过访问多个页面获取完整cookies")
            except Exception as e:
                logging.error(f"尝试获取完整cookies时出错: {e}")
        
        # 再次检查_xsrf字段
        if '_xsrf' in cookies_dict:
            xsrf = cookies_dict['_xsrf']
            parts = xsrf.split('|')
            if len(parts) < 4:
                logging.warning(f"_xsrf格式不正确: {xsrf}，可能无法正确判断过期时间")
            else:
                try:
                    timestamp = int(parts[3])
                    expiry_date = datetime.datetime.fromtimestamp(timestamp)
                    current_date = datetime.datetime.now()
                    days_to_expiry = (expiry_date - current_date).days
                    logging.info(f"获取的新cookies将在{days_to_expiry}天后过期")
                except Exception as e:
                    logging.warning(f"解析_xsrf中的过期时间出错: {e}")
        else:
            logging.warning("获取的新cookies中仍然缺少_xsrf字段，可能会影响过期时间检测")
            
        # 将cookies保存到文件
        cookies_path = os.path.join('data', 'cookies.txt')
        cookies_str = '; '.join([f"{name}={value}" for name, value in cookies_dict.items()])
        
        with open(cookies_path, 'w', encoding='utf-8') as f:
            f.write(cookies_str)
            
        logging.info("已获取新的cookies并保存到文件")
        return cookies_dict, headers
    except Exception as e:
        logging.error(f"更新cookies时出错: {e}")
        return None, None

def load_cookies():
    """从cookies.txt文件加载cookies"""
    try:
        cookies_path = os.path.join('data', 'cookies.txt')
        if not os.path.exists(cookies_path):
            logging.error(f"Cookies文件不存在: {cookies_path}")
            # 尝试自动更新cookies
            return update_cookies()
            
        with open(cookies_path, 'rb') as f:
            cookies_bytes = f.read()
            # 尝试不同的编码方式解码
            encodings = ['utf-8', 'utf-16', 'utf-16le', 'gbk', 'gb2312', 'ascii']
            cookies_str = None
            for encoding in encodings:
                try:
                    cookies_str = cookies_bytes.decode(encoding).strip()
                    logging.info(f"成功使用{encoding}编码解析cookies文件")
                    break
                except UnicodeDecodeError:
                    continue
            
            if cookies_str is None:
                logging.error("无法使用任何已知编码解析cookies文件")
                return update_cookies()
        
        # 解析cookies字符串为字典
        cookies_dict = {}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 分割cookies字符串并解析为字典
        for item in cookies_str.split(';'):
            if '=' in item:
                name, value = item.strip().split('=', 1)
                cookies_dict[name] = value
        
        # 检查token是否存在，用于判断cookies是否有效
        if 'token' not in cookies_dict:
            logging.error("Cookies中没有找到token")
            # 尝试自动更新cookies
            return update_cookies()
            
        # 检查_xsrf字段，它通常包含过期时间信息
        if '_xsrf' not in cookies_dict:
            logging.warning("Cookies中缺少过期时间信息，尝试更新cookies")
            return update_cookies()
            
        xsrf = cookies_dict['_xsrf']
        # 尝试从_xsrf中提取时间戳
        try:
            # _xsrf格式通常为: 2|ffc493a1|18404ccad881b1822f58a5db6c063ba1|1740763534
            parts = xsrf.split('|')
            if len(parts) >= 4:
                timestamp = int(parts[3])
                expiry_date = datetime.datetime.fromtimestamp(timestamp)
                current_date = datetime.datetime.now()
                
                # 如果过期时间在当前时间之前，则cookies已过期
                if expiry_date < current_date:
                    logging.warning(f"Cookies已过期! 过期时间: {expiry_date}")
                    # 尝试自动更新cookies
                    return update_cookies()
                
                # 如果过期时间在7天内，发出警告
                days_to_expiry = (expiry_date - current_date).days
                if days_to_expiry < 7:
                    logging.warning(f"Cookies即将在{days_to_expiry}天后过期，请及时更新")
                    # 如果过期时间在1天内，尝试自动更新
                    if days_to_expiry <= 1:
                        logging.warning("Cookies即将在1天内过期，尝试自动更新")
                        return update_cookies()
            else:
                logging.warning("_xsrf格式不正确，尝试更新cookies")
                return update_cookies()
        except Exception as e:
            logging.error(f"解析cookies过期时间出错: {e}")
            return update_cookies()
        
        logging.info("成功加载cookies")
        return cookies_dict, headers
    except Exception as e:
        logging.error(f"加载cookies时出错: {e}")
        return None, None

def fetch_jq_data():
    """获取聚宽数据"""
    if not is_trading_time():
        logging.info("当前不是交易时间")
        return False
    
    # 检查是否为特殊时间点，如果是则延迟30秒
    if is_special_time_point():
        logging.info("当前为关键时间点，延迟30秒后检查数据...")
        time.sleep(30)
    
    try:
        # 加载cookies
        cookies, headers = load_cookies()
        if not cookies or not headers:
            logging.error("无法加载cookies，请检查cookies.txt文件或手动更新cookies")
            return False
    except Exception as e:
        logging.error(f"加载cookies时出错: {e}")
        return False
    
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
            with open("data/jq_log_data.json", "w", encoding="utf-8") as f:
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

def check_cookies_status():
    """检查cookies状态并输出信息"""
    cookies, _ = load_cookies()
    if not cookies:
        logging.info("Cookies状态：无效或不存在")
        return
    
    if '_xsrf' in cookies:
        xsrf = cookies['_xsrf']
        try:
            parts = xsrf.split('|')
            if len(parts) >= 4:
                timestamp = int(parts[3])
                expiry_date = datetime.datetime.fromtimestamp(timestamp)
                current_date = datetime.datetime.now()
                
                days_to_expiry = (expiry_date - current_date).days
                hours_to_expiry = (expiry_date - current_date).total_seconds() / 3600
                
                if expiry_date < current_date:
                    logging.info("Cookies状态：已过期")
                elif days_to_expiry <= 1:
                    logging.info(f"Cookies状态：即将在{hours_to_expiry:.1f}小时后过期")
                elif days_to_expiry < 7:
                    logging.info(f"Cookies状态：将在{days_to_expiry}天后过期")
                else:
                    logging.info(f"Cookies状态：正常，将在{days_to_expiry}天后过期")
        except Exception as e:
            logging.error(f"检查cookies状态时出错: {e}")
    else:
        logging.info("Cookies状态：缺少过期时间信息")

def main():
    # 设置定时任务，每5分钟执行一次数据获取
    schedule.every(5).minutes.do(fetch_jq_data)
    # 设置定时任务，每10分钟检查一次cookies状态
    schedule.every(10).minutes.do(check_cookies_status)
    
    logging.info("开始运行数据获取程序...")
    # 立即执行一次数据获取和cookies状态检查
    fetch_jq_data()
    check_cookies_status()
    
    # 持续运行定时任务
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()