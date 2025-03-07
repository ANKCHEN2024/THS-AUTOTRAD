import os
import json
import base64
import getpass
from cryptography.fernet import Fernet
import logging

# 配置日志记录
log_file = 'logs/config_manager.log'
os.makedirs('logs', exist_ok=True)

file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

class ConfigManager:
    def __init__(self):
        self.config_dir = 'data'
        self.config_file = os.path.join(self.config_dir, 'config.json')
        self.key_file = os.path.join(self.config_dir, '.key')
        self.ensure_config_dir()
        self._load_or_create_key()
        
    def ensure_config_dir(self):
        """确保配置目录存在"""
        os.makedirs(self.config_dir, exist_ok=True)
    
    def _load_or_create_key(self):
        """加载或创建加密密钥"""
        try:
            if os.path.exists(self.key_file):
                with open(self.key_file, 'rb') as f:
                    self.key = f.read()
            else:
                self.key = Fernet.generate_key()
                with open(self.key_file, 'wb') as f:
                    f.write(self.key)
            self.cipher_suite = Fernet(self.key)
        except Exception as e:
            logger.error(f"加载或创建密钥时出错: {e}")
            raise
    
    def encrypt_value(self, value):
        """加密字符串值"""
        try:
            return self.cipher_suite.encrypt(value.encode()).decode()
        except Exception as e:
            logger.error(f"加密值时出错: {e}")
            raise
    
    def decrypt_value(self, encrypted_value):
        """解密字符串值"""
        try:
            return self.cipher_suite.decrypt(encrypted_value.encode()).decode()
        except Exception as e:
            logger.error(f"解密值时出错: {e}")
            raise
    
    def save_credentials(self, username, password):
        """保存加密后的凭据"""
        try:
            config = {
                'username': self.encrypt_value(username),
                'password': self.encrypt_value(password)
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
            logger.info("凭据已加密保存")
            return True
        except Exception as e:
            logger.error(f"保存凭据时出错: {e}")
            return False
    
    def load_credentials(self):
        """加载并解密凭据"""
        try:
            if not os.path.exists(self.config_file):
                logger.info("配置文件不存在，需要初始化凭据")
                return None, None
            
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            username = self.decrypt_value(config['username'])
            password = self.decrypt_value(config['password'])
            return username, password
        except Exception as e:
            logger.error(f"加载凭据时出错: {e}")
            return None, None
    
    def initialize_credentials(self):
        """初始化用户凭据"""
        try:
            print("\n=== 聚宽账号配置 ===")
            print("请输入您的聚宽账号信息（确保账号密码正确）：")
            username = input("用户名: ").strip()
            password = getpass.getpass("密码: ").strip()
            
            if not username or not password:
                logger.error("用户名或密码不能为空")
                print("\n错误：用户名或密码不能为空！")
                return False
            
            if self.save_credentials(username, password):
                print("\n凭据已成功保存！")
                return True
            return False
        except Exception as e:
            logger.error(f"初始化凭据时出错: {e}")
            print(f"\n错误：初始化凭据失败 - {e}")
            return False

def get_credentials():
    """获取凭据的便捷函数"""
    config_manager = ConfigManager()
    username, password = config_manager.load_credentials()
    
    # 如果没有找到凭据，进行初始化
    if username is None or password is None:
        if not config_manager.initialize_credentials():
            logger.error("初始化凭据失败")
            return None, None
        username, password = config_manager.load_credentials()
    
    return username, password

if __name__ == '__main__':
    # 测试配置管理器
    config_manager = ConfigManager()
    config_manager.initialize_credentials()