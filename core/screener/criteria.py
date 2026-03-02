"""Screening criteria data class."""

from dataclasses import dataclass, field


@dataclass
class ScreeningCriteria:
    # Financial filters
    pe_min: float = 0
    pe_max: float = 999
    market_cap_min: float = 0          # in USD
    market_cap_max: float | None = None
    revenue_growth_min: float | None = None

    # Options filters
    iv_rank_min: float = 0
    iv_rank_max: float = 100
    iv_hv_ratio_min: float | None = None
    min_option_volume: int = 0
    min_put_premium_yield: float = 0   # percentage

    # Technical filters
    min_stock_volume: int = 0
    price_above_ma: int | None = None  # e.g. 50 = price above MA50

    # Universe
    exchanges: list[str] = field(default_factory=lambda: ["NYSE", "NASDAQ"])
