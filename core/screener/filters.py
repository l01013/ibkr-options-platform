"""Screening filters: financial, IV, technical."""

from core.screener.criteria import ScreeningCriteria
from utils.logger import setup_logger

logger = setup_logger("screener_filters")


class FinancialFilter:
    """Filter stocks by PE ratio and market cap."""

    def apply(self, stock_data: dict, criteria: ScreeningCriteria) -> bool:
        pe = stock_data.get("pe_ratio")
        if pe is not None:
            if not (criteria.pe_min <= pe <= criteria.pe_max):
                return False

        mcap = stock_data.get("market_cap")
        if mcap is not None:
            if mcap < criteria.market_cap_min:
                return False
            if criteria.market_cap_max and mcap > criteria.market_cap_max:
                return False

        rev_growth = stock_data.get("revenue_growth")
        if criteria.revenue_growth_min is not None and rev_growth is not None:
            if rev_growth < criteria.revenue_growth_min:
                return False

        return True


class IVFilter:
    """Filter stocks by IV Rank, IV/HV ratio, option volume, put premium yield."""

    def apply(self, stock_data: dict, criteria: ScreeningCriteria) -> bool:
        iv_rank = stock_data.get("iv_rank")
        if iv_rank is not None:
            if not (criteria.iv_rank_min <= iv_rank <= criteria.iv_rank_max):
                return False

        if criteria.iv_hv_ratio_min is not None:
            iv_hv = stock_data.get("iv_hv_ratio")
            if iv_hv is not None and iv_hv < criteria.iv_hv_ratio_min:
                return False

        opt_vol = stock_data.get("option_volume", 0)
        if opt_vol < criteria.min_option_volume:
            return False

        put_yield = stock_data.get("put_premium_yield", 0)
        if put_yield < criteria.min_put_premium_yield:
            return False

        return True


class TechnicalFilter:
    """Filter stocks by volume and price/MA relationship."""

    def apply(self, stock_data: dict, criteria: ScreeningCriteria) -> bool:
        vol = stock_data.get("volume", 0)
        if vol < criteria.min_stock_volume:
            return False

        if criteria.price_above_ma is not None:
            price = stock_data.get("price", 0)
            ma_val = stock_data.get(f"ma{criteria.price_above_ma}", 0)
            if price and ma_val and price < ma_val:
                return False

        return True
