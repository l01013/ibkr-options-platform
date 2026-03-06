"""Internationalization (i18n) utilities for multi-language support."""

from typing import Dict

# Language translations dictionary
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        # Navbar
        "navbar.dashboard": "Dashboard",
        "navbar.market_data": "Market Data",
        "navbar.screener": "Screener",
        "navbar.options_chain": "Options Chain",
        "navbar.backtester": "Backtester",
        "navbar.settings": "Settings",
        "navbar.language": "Language",
        
        # Backtester
        "backtester.title": "Options Strategy Backtester",
        "backtester.config": "Backtest Configuration",
        "backtester.strategy": "Strategy",
        "backtester.symbol": "Symbol",
        "backtester.date_range": "Date Range",
        "backtester.initial_capital": "Initial Capital ($)",
        "backtester.max_leverage": "Max Leverage",
        "backtester.dte_range": "DTE Range (days)",
        "backtester.target_delta": "Target Delta (absolute)",
        "backtester.profit_target": "Profit Target (% of premium)",
        "backtester.stop_loss": "Stop Loss (% of premium)",
        "backtester.max_positions": "Max Positions",
        "backtester.benchmark": "Select Benchmarks",
        "backtester.wheel_params": "Wheel Strategy Parameters",
        "backtester.put_delta": "Put Delta (absolute)",
        "backtester.call_delta": "Call Delta (absolute)",
        "backtester.run": "Run Backtest",
        "backtester.performance_summary": "Performance Summary",
        "backtester.additional_metrics": "Additional Metrics",
        "backtester.trade_timeline": "Trade Timeline Analysis",
        "backtester.trade_log": "Trade Log",
        "backtester.no_trades": "No trades",
        "backtester.current_holdings": "Current Holdings",
        "backtester.position_management": "Position Management",
        "backtester.benchmark_comparison": "Benchmark Comparison",
        
        # Strategies
        "strategy.sell_put": "Sell Put (Cash Secured)",
        "strategy.covered_call": "Covered Call",
        "strategy.iron_condor": "Iron Condor",
        "strategy.bull_put_spread": "Bull Put Spread",
        "strategy.bear_call_spread": "Bear Call Spread",
        "strategy.straddle": "Straddle (Short)",
        "strategy.strangle": "Strangle (Short)",
        "strategy.wheel": "Wheel Strategy",
        
        # Benchmarks
        "benchmark.QQQ": "QQQ - Nasdaq-100 ETF",
        "benchmark.SPY": "SPY - S&P 500 ETF",
        "benchmark.IWM": "IWM - Russell 2000 ETF",
        "benchmark.NVDA": "NVDA - NVIDIA Corporation",
        "benchmark.TSLA": "TSLA - Tesla Inc",
        "benchmark.AAPL": "AAPL - Apple Inc",
        "benchmark.MSFT": "MSFT - Microsoft Corporation",
        "benchmark.GOOGL": "GOOGL - Alphabet Inc",
        "benchmark.AMZN": "AMZN - Amazon.com Inc",
    },
    "zh": {
        # Navbar
        "navbar.dashboard": "仪表盘",
        "navbar.market_data": "市场数据",
        "navbar.screener": "选股器",
        "navbar.options_chain": "期权链",
        "navbar.backtester": "回测器",
        "navbar.settings": "设置",
        "navbar.language": "语言",
        
        # Backtester
        "backtester.title": "期权策略回测器",
        "backtester.config": "回测配置",
        "backtester.strategy": "策略",
        "backtester.symbol": "标的",
        "backtester.date_range": "日期范围",
        "backtester.initial_capital": "初始资金 ($)",
        "backtester.max_leverage": "最大杠杆",
        "backtester.dte_range": "到期天数范围 (天)",
        "backtester.target_delta": "目标 Delta (绝对值)",
        "backtester.profit_target": "止盈目标 (% 权利金)",
        "backtester.stop_loss": "止损 (% 权利金)",
        "backtester.max_positions": "最大仓位数",
        "backtester.benchmark": "选择基准对比",
        "backtester.wheel_params": "Wheel 策略参数",
        "backtester.put_delta": "Put Delta (绝对值)",
        "backtester.call_delta": "Call Delta (绝对值)",
        "backtester.run": "运行回测",
        "backtester.performance_summary": "业绩汇总",
        "backtester.additional_metrics": "附加指标",
        "backtester.trade_timeline": "交易时间线分析",
        "backtester.trade_log": "交易日志",
        "backtester.no_trades": "无交易记录",
        "backtester.current_holdings": "当前持仓",
        "backtester.position_management": "仓位管理",
        "backtester.benchmark_comparison": "基准对比",
        
        # Strategies
        "strategy.sell_put": "卖出看跌期权 (现金担保)",
        "strategy.covered_call": "备兑看涨期权",
        "strategy.iron_condor": "铁鹰式套利",
        "strategy.bull_put_spread": "牛市看跌价差",
        "strategy.bear_call_spread": "熊市看涨价差",
        "strategy.straddle": "跨式套利 (空头)",
        "strategy.strangle": "宽跨式套利 (空头)",
        "strategy.wheel": "轮动策略",
        
        # Benchmarks
        "benchmark.QQQ": "QQQ - 纳斯达克 100ETF",
        "benchmark.SPY": "SPY - 标普 500ETF",
        "benchmark.IWM": "IWM - 罗素 2000ETF",
        "benchmark.NVDA": "NVDA - 英伟达",
        "benchmark.TSLA": "TSLA - 特斯拉",
        "benchmark.AAPL": "AAPL - 苹果",
        "benchmark.MSFT": "MSFT - 微软",
        "benchmark.GOOGL": "GOOGL - 谷歌",
        "benchmark.AMZN": "AMZN - 亚马逊",
    }
}


def get_translation(key: str, lang: str = "en") -> str:
    """Get translation for a given key and language.
    
    Args:
        key: Translation key (e.g., "navbar.dashboard")
        lang: Language code ("en" or "zh")
        
    Returns:
        Translated text, or English if translation not found
    """
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)


def create_language_middleware():
    """Create a middleware function for language-aware callbacks.
    
    Returns:
        Function that takes (lang, key) and returns translated text
    """
    def translate(lang: str, key: str) -> str:
        return get_translation(key, lang)
    
    return translate
