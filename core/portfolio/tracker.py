"""Portfolio tracker: tracks current positions and overall portfolio state."""

from dataclasses import dataclass, field


@dataclass
class PortfolioTracker:
    """Simple portfolio state tracker."""
    initial_capital: float = 100000.0
    cash: float = 100000.0
    positions: list = field(default_factory=list)

    @property
    def total_value(self) -> float:
        position_value = sum(
            p.get("marketValue", 0) for p in self.positions
        )
        return self.cash + position_value

    @property
    def pnl(self) -> float:
        return self.total_value - self.initial_capital

    @property
    def pnl_pct(self) -> float:
        if self.initial_capital > 0:
            return (self.pnl / self.initial_capital) * 100
        return 0.0

    def update_positions(self, positions: list[dict]):
        self.positions = positions

    def update_cash(self, cash: float):
        self.cash = cash
