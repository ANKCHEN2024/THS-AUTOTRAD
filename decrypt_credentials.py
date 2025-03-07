import os
import json
from cryptography.fernet import Fernet

try:
    # 读取密钥
    with open('data/.key', 'rb') as f:
        key = f.read()
    
    # 读取加密的凭据
    with open('data/config.json', 'r') as f:
        config = json.load(f)
    
    # 解密
    cipher_suite = Fernet(key)
    username = cipher_suite.decrypt(config['username'].encode()).decode()
    password = cipher_suite.decrypt(config['password'].encode()).decode()
    
    # 显示解密后的凭据
    print('\n解密后的凭据:')
    print(f'用户名: {username}')
    print(f'密码: {password}\n')
except Exception as e:
    print(f'错误: {e}')