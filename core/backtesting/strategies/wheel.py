"""Wheel Strategy: cycles between Sell Put and Covered Call.

Phase 1 (SP): Sell OTM puts, collect premium
  - If expires worthless: keep premium, continue selling puts
  - If assigned: buy shares at strike, switch to Phase 2

Phase 2 (CC): Sell OTM calls against owned shares
  - If expires worthless: keep premium + shares, continue selling calls
  - If assigned: sell shares at strike, return to Phase 1
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from core.backtesting.strategies.base import BaseStrategy, Signal
from core.backtesting.pricing import OptionsPricer


@dataclass
class StockHolding:
    """Tracks stock position from put assignment."""
    shares: int = 0
    cost_basis: float = 0.0  # average cost per share
    total_premium_collected: float = 0.0  # cumulative premium from both phases


class WheelStrategy(BaseStrategy):
    """Wheel strategy implementation with state machine."""

    def __init__(self, params: dict):
        super().__init__(params)
        self.phase = "SP"  # Start with Sell Put phase
        self.stock_holding = StockHolding()
        self.put_delta = params.get("put_delta", 0.30)
        self.call_delta = params.get("call_delta", 0.30)
        # Track pending assignments
        self._pending_assignment = None

    @property
    def name(self) -> str:
        return "wheel"

    def on_trade_closed(self, trade: dict):
        """Called by engine when a trade is closed. Updates internal state."""
        if trade.get("exit_reason") == "ASSIGNMENT":
            if trade.get("trade_type") == "WHEEL_PUT":
                # Put assigned: we bought shares at strike price
                strike = trade["strike"]
                quantity = abs(trade["quantity"])
                shares_acquired = quantity * 100
                
                # Update stock holding
                total_cost = self.stock_holding.shares * self.stock_holding.cost_basis
                total_cost += shares_acquired * strike
                self.stock_holding.shares += shares_acquired
                if self.stock_holding.shares > 0:
                    self.stock_holding.cost_basis = total_cost / self.stock_holding.shares
                
                # Adjust cost basis by premium collected
                premium_collected = trade["entry_price"] * shares_acquired
                self.stock_holding.total_premium_collected += premium_collected
                
                # Switch to Covered Call phase
                self.phase = "CC"
                
            elif trade.get("trade_type") == "WHEEL_CALL":
                # Call assigned: we sold shares at strike price
                strike = trade["strike"]
                quantity = abs(trade["quantity"])
                shares_sold = quantity * 100
                
                # Reduce stock holding
                self.stock_holding.shares = max(0, self.stock_holding.shares - shares_sold)
                
                # Add premium to total collected
                premium_collected = trade["entry_price"] * shares_sold
                self.stock_holding.total_premium_collected += premium_collected
                
                # If no more shares, switch back to Sell Put phase
                if self.stock_holding.shares == 0:
                    self.phase = "SP"
                    self.stock_holding.cost_basis = 0.0
        else:
            # For non-assignment exits (profit target, stop loss, expiry worthless)
            # Just collect the premium difference
            if trade.get("trade_type") in ("WHEEL_PUT", "WHEEL_CALL"):
                # Premium is already accounted for in PnL
                pass

    def generate_signals(
        self,
        current_date: str,
        underlying_price: float,
        iv: float,
        open_positions: list,
    ) -> list[Signal]:
        """Generate signals based on current phase."""
        max_pos = self.params.get("max_positions", 1)
        
        # Check if we already have an open position
        wheel_positions = [
            p for p in open_positions 
            if p.trade_type in ("WHEEL_PUT", "WHEEL_CALL")
        ]
        if len(wheel_positions) >= max_pos:
            return []

        T = self.select_expiry_dte() / 365.0
        dte_days = int(self.select_expiry_dte())
        entry = datetime.strptime(current_date, "%Y-%m-%d")
        expiry_date = entry + timedelta(days=dte_days)
        expiry_str = expiry_date.strftime("%Y%m%d")

        if self.phase == "SP":
            return self._generate_sell_put_signal(
                underlying_price, iv, T, expiry_str
            )
        else:  # phase == "CC"
            return self._generate_covered_call_signal(
                underlying_price, iv, T, expiry_str
            )

    def _generate_sell_put_signal(
        self,
        underlying_price: float,
        iv: float,
        T: float,
        expiry_str: str,
    ) -> list[Signal]:
        """Generate Sell Put signal for Phase 1."""
        # Use put-specific delta
        original_delta = self.delta_target
        self.delta_target = self.put_delta
        strike = self.select_strike(underlying_price, iv, T, "P")
        self.delta_target = original_delta

        premium = OptionsPricer.put_price(underlying_price, strike, T, iv)
        delta = OptionsPricer.delta(underlying_price, strike, T, iv, "P")

        # Position sizing: cash secured put requires cash = strike * 100 per contract
        available_capital = self.initial_capital * self.position_percentage
        leveraged_capital = available_capital * self.max_leverage
        max_contracts = int(leveraged_capital / (strike * 100))
        max_contracts = max(1, min(max_contracts, self.params.get("max_positions", 1)))
        quantity = -max_contracts  # Sell

        return [Signal(
            symbol=self.params["symbol"],
            trade_type="WHEEL_PUT",
            right="P",
            strike=strike,
            expiry=expiry_str,
            quantity=quantity,
            iv=iv,
            delta=delta,
            premium=premium,
        )]

    def _generate_covered_call_signal(
        self,
        underlying_price: float,
        iv: float,
        T: float,
        expiry_str: str,
    ) -> list[Signal]:
        """Generate Covered Call signal for Phase 2."""
        # Can only sell calls for shares we own
        if self.stock_holding.shares <= 0:
            # Shouldn't happen, but fallback to SP phase
            self.phase = "SP"
            return self._generate_sell_put_signal(underlying_price, iv, T, expiry_str)

        # Use call-specific delta
        original_delta = self.delta_target
        self.delta_target = self.call_delta
        strike = self.select_strike(underlying_price, iv, T, "C")
        self.delta_target = original_delta

        premium = OptionsPricer.call_price(underlying_price, strike, T, iv)
        delta = OptionsPricer.delta(underlying_price, strike, T, iv, "C")

        # Covered call: 1 contract per 100 shares owned
        max_contracts = self.stock_holding.shares // 100
        max_contracts = max(1, min(max_contracts, self.params.get("max_positions", 1)))
        quantity = -max_contracts  # Sell

        return [Signal(
            symbol=self.params["symbol"],
            trade_type="WHEEL_CALL",
            right="C",
            strike=strike,
            expiry=expiry_str,
            quantity=quantity,
            iv=iv,
            delta=delta,
            premium=premium,
        )]

    def get_state_summary(self) -> dict:
        """Return current strategy state for debugging/display."""
        return {
            "phase": self.phase,
            "shares_held": self.stock_holding.shares,
            "cost_basis": round(self.stock_holding.cost_basis, 2),
            "total_premium_collected": round(self.stock_holding.total_premium_collected, 2),
            "effective_cost_basis": round(
                self.stock_holding.cost_basis - 
                (self.stock_holding.total_premium_collected / self.stock_holding.shares 
                 if self.stock_holding.shares > 0 else 0), 2
            ),
        }
