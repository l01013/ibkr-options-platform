"""Abstract base class for all options strategies."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class Signal:
    """Signal to open a new position."""
    symbol: str
    trade_type: str      # SELL_PUT, COVERED_CALL, etc.
    right: str           # P or C
    strike: float
    expiry: str          # YYYYMMDD
    quantity: int         # negative for sell
    iv: float
    delta: float
    premium: float       # expected premium per share


class BaseStrategy(ABC):
    """Abstract base for options strategies."""

    def __init__(self, params: dict):
        self.params = params
        self.dte_min = params.get("dte_min", 21)
        self.dte_max = params.get("dte_max", 45)
        self.delta_target = params.get("delta_target", 0.30)
        self.profit_target_pct = params.get("profit_target_pct", 50)
        self.stop_loss_pct = params.get("stop_loss_pct", 200)

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def generate_signals(
        self,
        current_date: str,
        underlying_price: float,
        iv: float,
        open_positions: list,
    ) -> list[Signal]:
        """Generate trading signals for the current date."""
        ...

    def select_strike(
        self,
        underlying_price: float,
        iv: float,
        T: float,
        right: str,
    ) -> float:
        """Select strike price based on target delta."""
        from core.backtesting.pricing import OptionsPricer
        # Binary search for the strike that gives target delta
        if right == "P":
            target_delta = -abs(self.delta_target)
            low = underlying_price * 0.7
            high = underlying_price * 1.0
        else:
            target_delta = abs(self.delta_target)
            low = underlying_price * 1.0
            high = underlying_price * 1.3

        for _ in range(50):
            mid = (low + high) / 2
            d = OptionsPricer.delta(underlying_price, mid, T, iv, right)
            if right == "P":
                if d < target_delta:
                    low = mid
                else:
                    high = mid
            else:
                if d > target_delta:
                    low = mid
                else:
                    high = mid
            if abs(d - target_delta) < 0.005:
                break

        # Round to nearest 0.5 or 1.0
        if underlying_price > 100:
            return round(mid)
        return round(mid * 2) / 2

    def select_expiry_dte(self) -> float:
        """Return target DTE in the middle of the range."""
        return (self.dte_min + self.dte_max) / 2
