# 同花顺自动化交易助手

## 项目简介
本项目是一个基于Python的同花顺自动化交易系统，能够自动监控交易信号、执行交易操作，实现自动化交易流程。

## 系统功能
- 自动启动同花顺客户端
- 自动登录交易界面
- 实时监控交易信号
- 自动执行买入/卖出操作
- 交易日志记录和分析

## 环境配置
### 1. 系统要求
- Windows操作系统
- Python 3.8或以上版本
- 同花顺客户端（已安装并配置）

### 2. 安装步骤
```bash
# 使用指定的Python解释器创建虚拟环境
C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe -m venv venv

# 激活虚拟环境(Windows)
.\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

注意：如果您的Python安装路径不同，请相应调整上述命令中的Python路径。

## 使用方法
### 1. 启动监控系统
```bash
# 直接运行批处理文件
start_monitor.bat
```
启动后系统会自动：
- 启动同花顺客户端
- 开始监控交易信号
- 执行自动化交易

### 2. 交易信号提取
```bash
# 激活虚拟环境
.\venv\Scripts\activate

# 提取交易信号
python extract_trade_signals.py
```

### 3. 手动执行交易
```bash
# 激活虚拟环境
.\venv\Scripts\activate

# 执行交易
python trade_executor.py
```

## 功能模块说明
### 1. open_ths_client.py
- 负责启动同花顺客户端
- 自动打开交易界面
- 处理客户端异常情况

### 2. extract_trade_signals.py
- 从日志中提取交易信号
- 解析买入/卖出指令
- 记录交易信息

### 3. trade_executor.py
- 执行自动化交易
- 处理买入/卖出操作
- 记录交易执行结果

### 4. trade_window_control.py
- 控制交易窗口
- 处理界面切换
- 管理交易模式

## 注意事项
1. 使用前请确保同花顺客户端已正确安装在默认路径（D:\同花顺）
2. 首次运行前需完成环境配置和依赖安装
3. 请确保系统有足够的权限执行自动化操作
4. 建议在使用前先进行小规模测试

## 日志说明
系统会在logs目录下生成以下日志文件：
- ths_client.log: 客户端操作日志
- extract_signals.log: 信号提取日志
- trade_executor.log: 交易执行日志
- trade_window.log: 窗口操作日志

## 数据文件
系统在data目录下维护以下数据文件：
- jq_log_data.json: 原始交易日志
- trade_signals.json: 提取的交易信号

## 安全提示
1. 请勿在公共环境下保存交易账户信息
2. 建议定期检查日志文件，及时发现异常
3. 使用自动化交易时需谨慎，建议设置合理的交易限额