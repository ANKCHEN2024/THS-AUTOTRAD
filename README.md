# 同花顺自动化交易助手

这个项目提供了一套自动化工具，用于获取聚宽量化交易平台的模拟策略日志信息，并通过同花顺客户端实现自动化交易操作。

## 项目文件说明

- `get_jq_data.py`: 从聚宽平台获取策略日志数据的脚本
- `jq_log_data.json`: 保存的策略日志数据
- `extract_trade_signals.py`: 从日志数据中提取交易信号
- `trade_signals.json`: 提取的交易信号数据
- `trade_executor.py`: 执行自动化交易的核心模块
- `trade_window_control.py`: 控制同花顺交易窗口的功能模块
- `open_ths_client.py`: 打开同花顺客户端和交易界面
- `cookies.txt`: 存储访问聚宽平台的cookie信息
- `ths_client.log`: 同花顺客户端操作日志
- `trade_executor.log`: 交易执行日志
- `requirements.txt`: 项目依赖包列表
- `venv/`: Python虚拟环境

## 环境配置

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境(Windows)
.\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

## 使用方法

### 1. 获取聚宽策略日志

```bash
# 激活虚拟环境
.\venv\Scripts\activate

# 运行数据获取脚本
python get_jq_data.py
```

### 2. 提取交易信号

```bash
# 激活虚拟环境
.\venv\Scripts\activate

# 提取交易信号
python extract_trade_signals.py
```

### 3. 执行自动化交易

```bash
# 激活虚拟环境
.\venv\Scripts\activate

# 打开同花顺客户端并执行交易
python trade_executor.py
```

如果同花顺安装在非默认路径，可以在open_ths_client.py中修改路径：

```python
client_hexin = THSClient("D:\自定义路径\同花顺\xiadan.exe")
```

## 注意事项

- 使用前需要先登录聚宽平台获取有效的cookie信息
- 确保同花顺客户端已正确安装并能正常登录
- 所有操作前请确保已激活虚拟环境
- 自动化交易过程中请勿手动操作鼠标和键盘
- 建议在执行自动化交易前先进行小额测试
- 请确保网络连接稳定，以保证数据获取和交易执行的可靠性