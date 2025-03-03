# 聚宽量化交易数据获取工具

这个项目用于获取聚宽量化交易平台的模拟策略日志信息，并提供同花顺客户端自动化操作功能。

## 项目文件说明

- `get_jq_data.py`: 从聚宽平台获取策略日志数据的脚本
- `jq_log_data.json`: 保存的策略日志数据
- `extract_trade_signals.py`: 从日志数据中提取交易信号
- `open_ths_client.py`: 打开同花顺客户端和交易界面
- `install_dependencies.py`: 安装项目依赖包
- `cookies.txt`: 存储访问聚宽平台的cookie信息
- `venv/`: Python虚拟环境
- `reports/`: 报告存放目录

## 环境配置

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境(Windows)
.\venv\Scripts\activate

# 安装依赖
python install_dependencies.py
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

### 3. 打开同花顺客户端

```bash
# 激活虚拟环境
.\venv\Scripts\activate

# 打开同花顺客户端
python open_ths_client.py
```

如果同花顺安装在非默认路径，可以指定路径：

```bash
python open_ths_client.py "D:\自定义路径\同花顺\xiadan.exe"
```

## 注意事项

- 使用前需要先登录聚宽平台获取有效的cookie信息
- 使用同花顺自动化功能需要准备交易按钮的截图(trading_button.png)用于图像识别
- 所有操作前请确保已激活虚拟环境 