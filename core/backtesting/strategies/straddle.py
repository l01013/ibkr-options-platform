"""Straddle and Strangle strategies (short)."""

from core.backtesting.strategies.base import BaseStrategy, Signal
from core.backtesting.pricing import OptionsPricer
from datetime import datetime, timedelta


class StraddleStrategy(BaseStrategy):
    """Short straddle: sell ATM put + sell ATM call."""

    @property
    def name(self) -> str:
        return "straddle"

    def generate_signals(
        self,
        current_date: str,
        underlying_price: float,
        iv: float,
        open_positions: list,
    ) -> list[Signal]:
        max_pos = self.params.get("max_positions", 1)
        if len(open_positions) >= max_pos:
            return []

        T = self.select_expiry_dte() / 365.0
        dte_days = int(self.select_expiry_dte())
        entry = datetime.strptime(current_date, "%Y-%m-%d")
        expiry_date = entry + timedelta(days=dte_days)
        expiry_str = expiry_date.strftime("%Y%m%d")

        # ATM strike
        if underlying_price > 100:
            strike = round(underlying_price)
        else:
            strike = round(underlying_price * 2) / 2

        put_premium = OptionsPricer.put_price(underlying_price, strike, T, iv)
        call_premium = OptionsPricer.call_price(underlying_price, strike, T, iv)
        put_delta = OptionsPricer.delta(underlying_price, strike, T, iv, "P")
        call_delta = OptionsPricer.delta(underlying_price, strike, T, iv, "C")

        symbol = self.params["symbol"]
        return [
            Signal(symbol=symbol, trade_type="STRADDLE_PUT", right="P",
                   strike=strike, expiry=expiry_str, quantity=-1,
                   iv=iv, delta=put_delta, premium=put_premium),
            Signal(symbol=symbol, trade_type="STRADDLE_CALL", right="C",
                   strike=strike, expiry=expiry_str, quantity=-1,
                   iv=iv, delta=call_delta, premium=call_premium),
        ]


class StrangleStrategy(BaseStrategy):
    """Short strangle: sell OTM put + sell OTM call."""

    @property
    def name(self) -> str:
        return "strangle"

    def __init__(self, params: dict):
        super().__init__(params)
        self.put_delta = params.get("put_delta_target", 0.20)
        self.call_delta = params.get("call_delta_target", 0.20)

    def generate_signals(
        self,
        current_date: str,
        underlying_price: float,
        iv: float,
        open_positions: list,
    ) -> list[Signal]:
        max_pos = self.params.get("max_positions", 1)
        if len(open_positions) >= max_pos:
            return []

        T = self.select_expiry_dte() / 365.0
        dte_days = int(self.select_expiry_dte())
        entry = datetime.strptime(current_date, "%Y-%m-%d")
        expiry_date = entry + timedelta(days=dte_days)
        expiry_str = expiry_date.strftime("%Y%m%d")

        # OTM put
        saved = self.delta_target
        self.delta_target = self.put_delta
        put_strike = self.select_strike(underlying_price, iv, T, "P")
        self.delta_target = saved

        # OTM call
        saved = self.delta_target
        self.delta_target = self.call_delta
        call_strike = self.select_strike(underlying_price, iv, T, "C")
        self.delta_target = saved

        put_premium = OptionsPricer.put_price(underlying_price, put_strike, T, iv)
        call_premium = OptionsPricer.call_price(underlying_price, call_strike, T, iv)
        put_delta = OptionsPricer.delta(underlying_price, put_strike, T, iv, "P")
        call_delta = OptionsPricer.delta(underlying_price, call_strike, T, iv, "C")

        symbol = self.params["symbol"]
        return [
            Signal(symbol=symbol, trade_type="STRANGLE_PUT", right="P",
                   strike=put_strike, expiry=expiry_str, quantity=-1,
                   iv=iv, delta=put_delta, premium=put_premium),
            Signal(symbol=symbol, trade_type="STRANGLE_CALL", right="C",
                   strike=call_strike, expiry=expiry_str, quantity=-1,
                   iv=iv, delta=call_delta, premium=call_premium),
        ]
