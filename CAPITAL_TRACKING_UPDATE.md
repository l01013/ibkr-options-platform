# Trade Log 资本跟踪功能增强

## 📋 更新概览

为 Trade Log 增加了开仓和平仓时的总资金信息，使得交易者能够更好地分析资金变化对交易决策的影响。

---

## ✅ 完成的修改

### 1. 数据模型更新

#### `core/backtesting/simulator.py`

**OptionPosition 类新增字段：**
```python
@dataclass
class OptionPosition:
    # ... existing fields ...
    capital_at_entry: float = 0.0  # Total portfolio capital when opening position
```

**TradeRecord 类新增字段：**
```python
@dataclass
class TradeRecord:
    # ... existing fields ...
    capital_at_entry: float = 0.0      # Total capital when opening position
    capital_at_exit: float = 0.0       # Total capital when closing position
    
    def to_dict(self) -> dict:
        return {
            # ... existing fields ...
            "capital_at_entry": round(self.capital_at_entry, 2),
            "capital_at_exit": round(self.capital_at_exit, 2),
        }
```

#### `models/backtest.py`

**BacktestTrade 表新增列：**
```python
class BacktestTrade(Base):
    # ... existing columns ...
    capital_at_entry = Column(Float)       # total portfolio capital when opening position
    capital_at_exit = Column(Float)        # total portfolio capital when closing position
```

---

### 2. 回测引擎集成

#### `core/backtesting/engine.py`

**开仓时记录资金（第 ~150 行）：**
```python
pos = OptionPosition(
    symbol=sig.symbol,
    entry_date=bar_date,
    expiry=sig.expiry,
    strike=sig.strike,
    right=sig.right,
    trade_type=sig.trade_type,
    quantity=sig.quantity,
    entry_price=sig.premium,
    underlying_entry=underlying_price,
    iv_at_entry=sig.iv,
    delta_at_entry=sig.delta,
    capital_at_entry=position_mgr.net_capital,  # Record total capital at entry
)
```

**平仓时更新资金（第 ~96-106 行）：**
```python
for trade in closed:
    # Create position ID and release margin
    position_id = f"{trade.symbol}_{trade.entry_date}_{trade.strike}_{trade.right}"
    position_mgr.release_margin(position_id, trade.pnl)
    
    # Update trade record with capital information at exit
    trade.capital_at_exit = position_mgr.net_capital  # Record total capital after closing
    
    # Notify strategy of closed trade
    if hasattr(strategy, 'on_trade_closed'):
        strategy.on_trade_closed(trade.to_dict())
```

#### `core/backtesting/simulator.py`

**创建 TradeRecord 时传递资金信息（第 ~156-176 行）：**
```python
trade = TradeRecord(
    symbol=pos.symbol,
    trade_type=pos.trade_type,
    entry_date=pos.entry_date,
    exit_date=current_date,
    expiry=pos.expiry,
    strike=pos.strike,
    entry_price=pos.entry_price,
    exit_price=exit_price,
    quantity=pos.quantity,
    pnl=total_pnl,
    pnl_pct=total_pnl_pct,
    exit_reason=exit_reason,
    underlying_entry=pos.underlying_entry,
    underlying_exit=underlying_price,
    iv_at_entry=pos.iv_at_entry,
    delta_at_entry=pos.delta_at_entry,
    capital_at_entry=getattr(pos, 'capital_at_entry', 0.0),  # Pass from position
    capital_at_exit=0.0,  # Will be set by engine after margin release
)
```

---

## 📊 新增字段说明

### capital_at_entry（开仓标的总资金）

**定义**: 开仓时刻的投资组合总资金  
**计算**: `position_mgr.net_capital` 在开仓时的值  
**用途**: 
- 了解开仓时的资金规模
- 分析仓位大小与资金量的关系
- 评估资金管理策略

**示例**:
```json
{
  "symbol": "AAPL",
  "trade_type": "SELL_PUT",
  "entry_date": "2024-01-01",
  "strike": 150.0,
  "quantity": -1,
  "capital_at_entry": 100000.00
}
```

### capital_at_exit（平仓标的总资金）

**定义**: 平仓时刻的投资组合总资金  
**计算**: `position_mgr.net_capital` 在平仓后的值（已包含 P&L）  
**用途**:
- 了解平仓时的资金规模
- 计算该交易对总资金的贡献
- 分析交易期间的资金变化

**示例**:
```json
{
  "symbol": "AAPL",
  "trade_type": "SELL_PUT",
  "exit_date": "2024-01-15",
  "pnl": 300.00,
  "capital_at_exit": 100300.00
}
```

---

## 🔍 使用场景

### 1. 资金利用率分析

通过对比 `capital_at_entry` 和实际使用的保证金，可以计算：
- **资金利用率** = 保证金使用 / 总资金
- **闲置资金比例** = (总资金 - 保证金) / 总资金

### 2. 交易贡献度分析

通过 `capital_at_exit - capital_at_entry` 可以直观看到：
- 该交易期间总资金的变化
- 交易对整体收益的贡献
- 考虑复利效应的真实回报

### 3. 仓位管理优化

分析不同资金规模下的交易表现：
- 大资金时的仓位控制是否合理
- 小资金时是否过度交易
- 最优仓位百分比是多少

### 4. 回撤分析

结合多个交易的资金信息：
- 最大回撤发生的时间点
- 回撤期间的资金变化
- 恢复周期需要多久

---

## 📈 API 响应示例

### 交易历史 API

**请求**: `GET /api/backtest/123/trades`

**响应**:
```json
{
  "trades": [
    {
      "id": 1,
      "symbol": "AAPL",
      "trade_type": "SELL_PUT",
      "entry_date": "2024-01-01",
      "exit_date": "2024-01-15",
      "strike": 150.0,
      "entry_price": 5.00,
      "exit_price": 2.00,
      "quantity": -1,
      "pnl": 300.00,
      "pnl_pct": 2.0,
      "underlying_entry": 155.00,
      "underlying_exit": 158.00,
      "capital_at_entry": 100000.00,  // ← 新增
      "capital_at_exit": 100300.00     // ← 新增
    }
  ]
}
```

---

## 🧪 测试验证

运行测试脚本：
```bash
cd /mnt/harddisk/lwb/options-trading-platform
python3 test_capital_tracking.py
```

预期输出：
```
✅ TradeRecord capital fields test passed!
✅ OptionPosition capital field test passed!
✅ Default capital values test passed!

============================================================
All capital tracking tests passed! ✅
============================================================

New Trade Log Fields:
- capital_at_entry: Total portfolio capital when opening position
- capital_at_exit: Total portfolio capital when closing position

These fields will be available in:
- Backtest results API
- Trade history table
- Performance analytics
```

---

## 📝 数据库迁移

如果现有项目使用了 SQLite 数据库，需要添加新列：

```sql
ALTER TABLE backtest_trades ADD COLUMN capital_at_entry FLOAT;
ALTER TABLE backtest_trades ADD COLUMN capital_at_exit FLOAT;
```

或者删除旧的 database 文件重新创建（开发环境）：
```bash
rm data/trading.db
python3 -c "from models.base import Base; from models import *; Base.metadata.create_all()"
```

---

## 🎯 后续优化建议

### 1. 前端展示
在 Backtester 页面的交易历史表格中添加两列：
- "Capital @ Entry"
- "Capital @ Exit"

### 2. 性能分析
增加新的分析图表：
- 资金变化曲线（叠加交易进出点）
- 仓位大小与资金规模的关系图
- 资金利用率时间序列

### 3. 统计指标
计算额外的统计指标：
- 平均持仓时间内的资金增长率
- 不同资金规模下的胜率对比
- 资金周转率

---

## 📚 相关文件

### 修改的文件
- ✅ `core/backtesting/simulator.py` - 数据模型定义
- ✅ `core/backtesting/engine.py` - 资金记录逻辑
- ✅ `models/backtest.py` - 数据库模型

### 新增的文件
- ✅ `test_capital_tracking.py` - 单元测试
- ✅ `CAPITAL_TRACKING_UPDATE.md` - 本文档

---

## ✨ 总结

通过添加 `capital_at_entry` 和 `capital_at_exit` 两个字段，我们实现了：

1. ✅ **完整的资金跟踪**: 每个交易都有进出时的资金快照
2. ✅ **准确的收益分析**: 可以考虑资金规模变化的影响
3. ✅ **更好的决策支持**: 了解不同资金状态下的交易质量
4. ✅ **向后兼容**: 默认值为 0.0，不影响现有功能

这些改进使得回测系统更加专业，能够为实盘交易提供更可靠的参考数据！
