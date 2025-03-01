from pathlib import Path
from dotenv import load_dotenv
import os
import requests
import json

# 加载环境变量
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

class JQDataFetcher:
    def __init__(self):
        self.base_url = "https://www.joinquant.com"
        self.session = requests.Session()
        self.cookies = {}
        self._load_cookies()
    
    def _load_cookies(self):
        """从环境变量加载cookies"""
        cookie_str = os.getenv('JQ_COOKIES')
        if not cookie_str:
            raise ValueError("请在.env文件中设置JQ_COOKIES环境变量")
        
        # 解析cookies字符串
        for item in cookie_str.split(';'):
            if '=' in item:
                name, value = item.strip().split('=', 1)
                self.cookies[name] = value
        self.session.cookies.update(self.cookies)
    
    def get_trading_log(self, backtest_id, offset=-1):
        """获取交易日志数据
        
        Args:
            backtest_id (str): 回测ID
            offset (int): 数据偏移量，默认-1
        
        Returns:
            str: 交易日志数据文本
        """
        url = f"{self.base_url}/algorithm/live/log"
        params = {
            'backtestId': backtest_id,
            'offset': offset,
            'ajax': 1
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            # 尝试解析为JSON，如果成功则提取日志文本
            try:
                json_data = response.json()
                if isinstance(json_data, dict) and 'log' in json_data:
                    return json_data['log']
                return response.text
            except json.JSONDecodeError:
                # 如果不是JSON格式，直接返回文本内容
                return response.text
        except requests.exceptions.RequestException as e:
            raise Exception(f"获取交易数据失败: {str(e)}")