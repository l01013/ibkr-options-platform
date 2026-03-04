# IBKR Options Trading Platform

基于盈透证券 (Interactive Brokers) API 的美股期权交易平台，支持实时行情、股票筛选、多种期权策略回测，提供 Web 界面。

## 功能特性

- **实时行情** - 通过 IBKR API 获取美股实时报价和历史 K 线数据
- **期权链查看** - 查看完整期权链、Greeks (Delta/Gamma/Theta/Vega)、IV Smile 曲线
- **股票筛选器** - 按财务指标 (PE、市值)、期权 IV Rank、技术指标筛选股票
- **策略回测** - 支持 7 种期权策略回测，完整的收益指标和可视化
- **Web 界面** - 基于 Plotly Dash 的 6 页面 Web 应用
- **Docker 部署** - 一键部署（含 IB Gateway 容器）

### 支持的回测策略

| 策略 | 说明 |
|------|------|
| Sell Put | 卖出看跌期权（Cash Secured Put） |
| Covered Call | 备兑看涨期权 |
| Iron Condor | 铁鹰策略 |
| Bull Put Spread | 牛市看跌价差 |
| Bear Call Spread | 熊市看涨价差 |
| Short Straddle | 卖出跨式 |
| Short Strangle | 卖出宽跨式 |

## 技术栈

- **后端**: Python 3.11, ib_insync
- **前端**: Plotly Dash, Dash Bootstrap Components, AG Grid
- **期权定价**: Black-Scholes (scipy)
- **数据库**: SQLite + SQLAlchemy
- **部署**: Docker + Docker Compose

## 前提条件

1. **盈透证券账户** - 需要 IBKR 账户（支持 Paper Trading 模拟账户）
2. **API 权限** - 在 IBKR 账户管理页面启用 API 访问

## 快速开始

### 方式一：本地运行

#### 1. 安装 TWS 或 IB Gateway

从盈透官网下载并安装：
- [TWS (Trader Workstation)](https://www.interactivebrokers.com/en/trading/tws.php) - 完整交易客户端
- [IB Gateway](https://www.interactivebrokers.com/en/trading/ibgateway-stable.php) - 轻量版，无 GUI

#### 2. 登录并配置 API

1. 启动 TWS 或 IB Gateway，用 IBKR 账号登录
2. 配置 API 连接：
   - **TWS**: `Edit` -> `Global Configuration` -> `API` -> `Settings`
   - **IB Gateway**: 启动时自动配置
3. 确保以下选项已启用：
   - ✅ Enable ActiveX and Socket Clients
   - ✅ Allow connections from localhost only
4. 记住端口号：
   - Paper Trading: `7497` (TWS) 或 `4002` (Gateway)
   - Live Trading: `7496` (TWS) 或 `4001` (Gateway)

#### 3. 安装依赖并启动

```bash
# 克隆仓库
git clone https://github.com/buyanqifan/ibkr-options-platform.git
cd ibkr-options-platform

# 安装 Python 依赖
pip install -r requirements.txt

# 创建配置文件
cp .env.example .env

# 编辑配置（根据实际情况修改端口）
# IBKR_HOST=127.0.0.1
# IBKR_PORT=7497  # TWS Paper Trading
# IBKR_TRADING_MODE=paper

# 启动应用
PYTHONPATH=. python -m app.main
```

#### 4. 访问 Web 界面

浏览器打开 http://localhost:8050

在 **Settings** 页面点击 **Connect** 连接到 IBKR。

---

### 方式二：Docker 部署（推荐）

Docker 方式会自动启动 IB Gateway 容器，无需手动安装 TWS。

```bash
# 克隆仓库
git clone https://github.com/buyanqifan/ibkr-options-platform.git
cd ibkr-options-platform

# 创建配置文件
cp .env.example .env

# 编辑 .env，填入 IBKR 凭据
nano .env
```

**.env 文件内容：**
```env
# IBKR Credentials (for IB Gateway Docker)
USERNAME=你的 IBKR 用户名
PASSWORD='你的 IBKR 密码'  # 如果密码包含特殊字符，用单引号包裹

# IB Gateway Configuration
GATEWAY_OR_TWS=gateway
IBC_TradingMode=paper
IBC_ReadOnlyApi='no'
IBC_ExistingSessionDetectedAction=primaryonly
IBC_AutoRestart='yes'

# App Settings
IBKR_HOST=ibgateway
IBKR_PORT=8888
IBKR_CLIENT_ID=1
IBKR_TRADING_MODE=paper
APP_HOST=0.0.0.0
APP_PORT=8050
APP_DEBUG=false
DB_PATH=data/trading.db
LOG_LEVEL=INFO
```

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

浏览器打开 http://localhost:8050

## 页面功能

| 页面 | 功能说明 |
|------|---------|
| **Dashboard** | 连接状态、账户摘要（净值/现金/P&L）、当前持仓列表 |
| **Market Data** | 股票搜索、K 线图（支持 MA20/50/200）、实时报价 |
| **Screener** | 设置筛选条件（PE、市值、IV Rank 等），查看评分排名 |
| **Options Chain** | 期权链表格、Greeks 数据、IV Smile 曲线图 |
| **Backtester** | 策略选择、参数配置、P&L 曲线、月度热力图、交易记录 |
| **Settings** | IBKR 连接配置、手动连接/断开、缓存管理 |

## 项目结构

```
ibkr-options-platform/
├── app/                    # Dash Web 应用
│   ├── pages/              # 6 个页面
│   ├── components/         # 可复用组件（图表、表格）
│   └── main.py             # 应用入口
├── core/
│   ├── ibkr/               # IBKR 连接和数据获取
│   ├── market_data/        # 行情数据缓存
│   ├── screener/           # 股票筛选器
│   └── backtesting/        # 回测引擎和策略
├── models/                 # SQLAlchemy 数据模型
├── config/                 # 配置文件
├── utils/                  # 工具函数
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## 常见问题

### Q: 连接失败怎么办？

1. 确认 TWS/IB Gateway 已启动并登录
2. 检查端口号是否正确：
   - Paper Trading: `7497` (TWS) / `4002` (Gateway)
   - Live Trading: `7496` (TWS) / `4001` (Gateway)
3. 确认 TWS/Gateway 中 API 已启用且允许 localhost 连接
4. 检查防火墙设置

### Q: 没有 IBKR 账户能用吗？

可以！
- **回测功能** (Backtester) 不需要连接 IBKR，使用合成历史数据
- 可在 [IBKR 官网](https://www.interactivebrokers.com/) 申请免费的 Paper Trading 模拟账户

### Q: Paper Trading 和 Live Trading 有什么区别？

| 模式 | 说明 |
|------|------|
| Paper Trading | 模拟账户，虚拟资金，零风险，用于测试和学习 |
| Live Trading | 真实账户，真金白银，请谨慎操作 |

### Q: 市场数据有延迟吗？

- 默认获取的是延迟数据（15-20 分钟）
- 实时数据需要在 IBKR 账户中订阅市场数据服务

## 免责声明

本项目仅供学习和研究用途。期权交易存在风险，请在充分了解风险的情况下谨慎操作。作者不对使用本软件造成的任何损失负责。

## License

MIT
