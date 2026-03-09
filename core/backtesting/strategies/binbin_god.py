"""Binbin God Strategy: Dynamic MAG7 stock selection with Wheel strategy logic.

This strategy intelligently selects the best stock from MAG7 universe based on:
- P/E Ratio (20% weight) - Value stocks preferred
- Option IV (40% weight) - Higher premium income  
- Momentum (20% weight) - Positive trend
- Stability (20% weight) - Risk management

Then executes Wheel strategy logic (Sell Put phase only).
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Any
from core.backtesting.strategies.base import BaseStrategy, Signal
from core.backtesting.pricing import OptionsPricer
import logging


logger = logging.getLogger("binbin_god")


# MAG7 Universe
MAG7_STOCKS = ["MSFT", "AAPL", "NVDA", "GOOGL", "AMZN", "META", "TSLA"]


@dataclass
class StockScore:
    """Score for a single stock."""
    symbol: str
    pe_ratio: float
    iv_rank: float
    momentum: float
    stability: float
    total_score: float
    
    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "pe_ratio": self.pe_ratio,
            "iv_rank": self.iv_rank,
            "momentum": self.momentum,
            "stability": self.stability,
            "total_score": round(self.total_score, 2),
        }


class BinbinGodStrategy(BaseStrategy):
    """
    Binbin God Strategy - Intelligent stock selection + Wheel logic.
    
    Only implements Sell Put phase (simplified from full Wheel).
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.config = config
        self.symbol = config.get("symbol", "MAG7_AUTO")
        self.dte_min = config.get("dte_min", 30)
        self.dte_max = config.get("dte_max", 45)
        self.delta_target = config.get("delta_target", 0.30)
        self.profit_target_pct = config.get("profit_target_pct", 50)
        self.stop_loss_pct = config.get("stop_loss_pct", 200)
        self.max_positions = config.get("max_positions", 10)
        self.use_synthetic_data = config.get("use_synthetic_data", False)
        
        # Scoring weights
        self.weights = {
            "pe_ratio": 0.20,
            "iv_rank": 0.40,
            "momentum": 0.20,
            "stability": 0.20,
        }
        
        # Storage for MAG7 analysis
        self.mag7_analysis = {
            "ranked_stocks": [],
            "best_pick": None,
        }
    
    def _score_stocks(self, market_data: Dict[str, Any]) -> List[StockScore]:
        """Score all MAG7 stocks based on metrics."""
        scores = []
        
        for symbol in MAG7_STOCKS:
            # Get market data for this symbol
            if symbol not in market_data:
                continue
                
            data = market_data[symbol]
            
            # Extract metrics (use defaults if not available)
            pe_ratio = data.get("fundamentals", {}).get("pe_ratio", 25.0)
            iv_rank = data.get("options", {}).get("iv_rank", 50.0)
            momentum = data.get("technical", {}).get("momentum_score", 50.0)
            stability = data.get("technical", {}).get("stability_score", 50.0)
            
            # Normalize PE ratio (lower is better, invert the score)
            pe_score = max(0, min(100, 100 - pe_ratio))
            
            # Calculate weighted total score
            total_score = (
                pe_score * self.weights["pe_ratio"] +
                iv_rank * self.weights["iv_rank"] +
                momentum * self.weights["momentum"] +
                stability * self.weights["stability"]
            )
            
            scores.append(StockScore(
                symbol=symbol,
                pe_ratio=pe_ratio,
                iv_rank=iv_rank,
                momentum=momentum,
                stability=stability,
                total_score=total_score,
            ))
        
        # Sort by total score (descending)
        scores.sort(key=lambda x: x.total_score, reverse=True)
        return scores
    
    def _select_best_stock(self, market_data: Dict[str, Any]) -> str:
        """Select the best stock from MAG7 based on scoring."""
        scores = self._score_stocks(market_data)
        
        if not scores:
            logger.warning("No stocks scored, defaulting to NVDA")
            return "NVDA"
        
        # Store analysis results
        self.mag7_analysis["ranked_stocks"] = [s.to_dict() for s in scores]
        self.mag7_analysis["best_pick"] = scores[0].to_dict()
        
        best_symbol = scores[0].symbol
        logger.info(f"Selected {best_symbol} with score {scores[0].total_score:.1f}")
        
        return best_symbol
    
    def generate_signal(
        self,
        symbol: str,
        current_dt: datetime,
        bars: List[Dict],
        contracts: List[Dict],
        portfolio: Dict[str, Any],
        market_data: Dict[str, Any],
    ) -> Signal | None:
        """Generate trading signal for Binbin God strategy."""
        
        # If symbol is MAG7_AUTO, select the best stock
        if self.symbol == "MAG7_AUTO":
            actual_symbol = self._select_best_stock(market_data)
        else:
            actual_symbol = self.symbol
        
        # Check if we already have max positions
        current_positions = len(portfolio.get("positions", []))
        if current_positions >= self.max_positions:
            logger.debug(f"Max positions ({self.max_positions}) reached")
            return None
        
        # Filter for puts with target DTE and delta
        target_dte_mid = (self.dte_min + self.dte_max) / 2
        suitable_contracts = []
        
        for contract in contracts:
            if contract.get("right", "") != "P":
                continue
            
            # Check DTE
            dte = (contract.get("expiry", current_dt).date() - current_dt.date()).days if isinstance(contract.get("expiry"), datetime) else 0
            if not (self.dte_min <= dte <= self.dte_max):
                continue
            
            # Check delta (absolute value)
            delta = abs(contract.get("delta", 0))
            if 0.25 <= delta <= 0.35:  # Allow some flexibility around target
                suitable_contracts.append((contract, abs(delta - self.delta_target)))
        
        if not suitable_contracts:
            logger.debug(f"No suitable put contracts found for {actual_symbol}")
            return None
        
        # Select contract closest to target delta
        suitable_contracts.sort(key=lambda x: x[1])
        selected_contract = suitable_contracts[0][0]
        
        # Calculate position size (1 contract per $10k capital as rough guide)
        capital = portfolio.get("cash", 100000)
        max_contracts_by_capital = int(capital / 10000)
        max_contracts_by_limit = self.max_positions - current_positions
        quantity = min(max_contracts_by_capital, max_contracts_by_limit, 10)
        
        if quantity <= 0:
            return None
        
        logger.info(f"Selling {quantity} put(s) on {actual_symbol} @ ${selected_contract.get('bid', 0):.2f}")
        
        return Signal(
            action="SELL_PUT",
            symbol=actual_symbol,
            contract=selected_contract,
            quantity=quantity,
            price=selected_contract.get("bid", 0),
        )
    
    def should_exit_position(
        self,
        position: Dict[str, Any],
        current_price: float,
        entry_price: float,
        current_dt: datetime,
    ) -> tuple[bool, str]:
        """Check if position should be exited."""
        
        # Calculate P&L
        pnl = current_price - entry_price
        pnl_pct = (pnl / entry_price) * 100 if entry_price > 0 else 0
        
        # Profit target exit
        profit_threshold = self.profit_target_pct / 100.0 * entry_price
        if pnl <= -profit_threshold:  # Premium decayed enough
            return True, "PROFIT_TARGET"
        
        # Stop loss exit
        loss_threshold = self.stop_loss_pct / 100.0 * entry_price
        if pnl >= loss_threshold:  # Loss exceeded threshold
            return True, "STOP_LOSS"
        
        # Expiry exit
        expiry = position.get("expiry")
        if expiry and current_dt >= expiry:
            return True, "EXPIRY"
        
        return False, ""
    
    def get_mag7_analysis(self) -> Dict[str, Any]:
        """Get MAG7 analysis results."""
        return self.mag7_analysis
