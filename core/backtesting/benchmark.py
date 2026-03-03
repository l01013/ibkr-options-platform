"""Benchmark data service for comparing strategy performance against market indices and stocks."""

from typing import List, Dict, Optional
import numpy as np
from datetime import datetime
from core.ibkr.data_client import IBKRDataClient
from utils.logger import setup_logger

logger = setup_logger("benchmark_service")


class BenchmarkService:
    """Service for fetching and calculating benchmark performance data."""
    
    # Common benchmark symbols
    BENCHMARK_SYMBOLS = {
        "QQQ": "Nasdaq-100 ETF",
        "SPY": "S&P 500 ETF", 
        "IWM": "Russell 2000 ETF",
        "NVDA": "NVIDIA Corporation",
        "TSLA": "Tesla Inc",
        "AAPL": "Apple Inc",
        "MSFT": "Microsoft Corporation",
        "GOOGL": "Alphabet Inc",
        "AMZN": "Amazon.com Inc",
    }
    
    def __init__(self, data_client: Optional[IBKRDataClient] = None):
        self._data_client = data_client
        self._cache = {}  # Simple in-memory cache
        
    def get_benchmark_options(self) -> List[Dict[str, str]]:
        """Get available benchmark options for UI selection."""
        return [
            {"value": symbol, "label": f"{symbol} - {name}"}
            for symbol, name in self.BENCHMARK_SYMBOLS.items()
        ]
    
    def get_benchmark_performance(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str,
        initial_capital: float = 100000.0
    ) -> Optional[List[Dict]]:
        """Calculate benchmark performance data for buy-and-hold strategy.
        
        Returns list of daily performance data with dates and cumulative returns.
        """
        cache_key = f"{symbol}_{start_date}_{end_date}_{initial_capital}"
        
        # Check cache first
        if cache_key in self._cache:
            logger.info(f"Using cached benchmark data for {symbol}")
            return self._cache[cache_key]
            
        if not self._data_client:
            logger.warning("No data client available, returning None")
            return None
            
        try:
            # Fetch historical data
            bars = self._data_client.get_historical_bars(
                symbol=symbol,
                duration=self._calculate_duration(start_date, end_date),
                bar_size="1 day"
            )
            
            if not bars:
                logger.warning(f"No data found for {symbol}")
                return None
                
            # Filter to date range
            filtered_bars = [
                bar for bar in bars 
                if start_date <= bar["date"][:10] <= end_date
            ]
            
            if not filtered_bars:
                logger.warning(f"No data in date range for {symbol}")
                return None
                
            # Calculate buy-and-hold performance
            performance_data = self._calculate_buy_and_hold_performance(
                filtered_bars, initial_capital
            )
            
            # Cache the result
            self._cache[cache_key] = performance_data
            logger.info(f"Calculated benchmark performance for {symbol}: {len(performance_data)} data points")
            
            return performance_data
            
        except Exception as e:
            logger.error(f"Error fetching benchmark data for {symbol}: {e}")
            return None
    
    def _calculate_duration(self, start_date: str, end_date: str) -> str:
        """Calculate appropriate duration string for IBKR API."""
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end - start).days
        
        if days <= 365:
            return "1 Y"
        elif days <= 730:
            return "2 Y"
        else:
            return f"{min(days // 365 + 1, 5)} Y"
    
    def _calculate_buy_and_hold_performance(
        self, 
        bars: List[Dict], 
        initial_capital: float
    ) -> List[Dict]:
        """Calculate buy-and-hold performance from historical price data."""
        if not bars:
            return []
            
        # Get initial price (first bar)
        initial_price = bars[0]["close"]
        if initial_price <= 0:
            logger.warning("Invalid initial price, cannot calculate performance")
            return []
            
        # Calculate shares that could be bought
        shares = initial_capital / initial_price
        
        performance_data = []
        for bar in bars:
            current_price = bar["close"]
            current_value = shares * current_price
            cumulative_pnl = current_value - initial_capital
            percentage_return = (cumulative_pnl / initial_capital) * 100
            
            performance_data.append({
                "date": bar["date"][:10],  # YYYY-MM-DD
                "price": current_price,
                "value": round(current_value, 2),
                "cumulative_pnl": round(cumulative_pnl, 2),
                "percentage_return": round(percentage_return, 2),
                "shares": shares
            })
            
        return performance_data
    
    def get_multiple_benchmarks(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        initial_capital: float = 100000.0
    ) -> Dict[str, List[Dict]]:
        """Get performance data for multiple benchmarks."""
        results = {}
        for symbol in symbols:
            performance = self.get_benchmark_performance(
                symbol, start_date, end_date, initial_capital
            )
            if performance:
                results[symbol] = performance
        return results
    
    def clear_cache(self):
        """Clear the benchmark data cache."""
        self._cache.clear()
        logger.info("Benchmark cache cleared")