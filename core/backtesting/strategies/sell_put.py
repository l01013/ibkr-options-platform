"""Sell Put (Cash Secured Put) strategy."""

from core.backtesting.strategies.base import BaseStrategy, Signal
from core.backtesting.pricing import OptionsPricer
from datetime import datetime, timedelta


class SellPutStrategy(BaseStrategy):

    @property
    def name(self) -> str:
        return "sell_put"

    def generate_signals(
        self,
        current_date: str,
        underlying_price: float,
        iv: float,
        open_positions: list,
        position_mgr=None,
    ) -> list[Signal]:
        max_pos = self.params.get("max_positions", 1)
        if len(open_positions) >= max_pos:
            return []

        T = self.select_expiry_dte() / 365.0
        strike = self.select_strike(underlying_price, iv, T, "P")
        premium = OptionsPricer.put_price(underlying_price, strike, T, iv)
        delta = OptionsPricer.delta(underlying_price, strike, T, iv, "P")

        # Calculate position size using position manager if available
        if position_mgr:
            # Use position manager for capital-aware sizing
            margin_per_contract = strike * 100  # Cash-secured put requirement
            num_contracts = position_mgr.calculate_position_size(
                margin_per_contract=margin_per_contract,
                max_positions=max_pos,
            )
            # Return empty if insufficient capital
            if num_contracts <= 0:
                return []
        else:
            # Fallback to legacy calculation (backward compatibility)
            available_capital = self.initial_capital * self.position_percentage
            leveraged_capital = available_capital * self.max_leverage
            
            max_contracts_by_capital = int(leveraged_capital / (strike * 100))
            
            # For risk-based sizing, use premium income as the measure
            expected_premium_income = premium * 100
            max_contracts_by_risk = int((self.initial_capital * self.max_risk_per_trade) / expected_premium_income) if expected_premium_income > 0 else max_pos
            
            num_contracts = min(max_pos, max_contracts_by_capital, max_contracts_by_risk)
            
            # Return 0 if insufficient capital (no forced position sizing)
            # This ensures realistic backtest results
            if num_contracts <= 0:
                return []
        
        quantity = -num_contracts  # Sell contracts (negative quantity)

        dte_days = int(self.select_expiry_dte())
        entry = datetime.strptime(current_date, "%Y-%m-%d")
        expiry_date = entry + timedelta(days=dte_days)
        expiry_str = expiry_date.strftime("%Y%m%d")

        return [Signal(
            symbol=self.params["symbol"],
            trade_type="SELL_PUT",
            right="P",
            strike=strike,
            expiry=expiry_str,
            quantity=quantity,
            iv=iv,
            delta=delta,
            premium=premium,
        )]
