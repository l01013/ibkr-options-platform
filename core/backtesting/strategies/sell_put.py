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
    ) -> list[Signal]:
        max_pos = self.params.get("max_positions", 1)
        if len(open_positions) >= max_pos:
            return []

        T = self.select_expiry_dte() / 365.0
        strike = self.select_strike(underlying_price, iv, T, "P")
        premium = OptionsPricer.put_price(underlying_price, strike, T, iv)
        delta = OptionsPricer.delta(underlying_price, strike, T, iv, "P")

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
            quantity=-1,
            iv=iv,
            delta=delta,
            premium=premium,
        )]
