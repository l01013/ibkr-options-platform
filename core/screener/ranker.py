"""Screening ranker: multi-dimensional weighted scoring."""


class ScreeningRanker:
    """Score and rank screened stocks from 0-100."""

    def __init__(
        self,
        iv_rank_weight: float = 0.35,
        put_yield_weight: float = 0.30,
        financial_weight: float = 0.20,
        liquidity_weight: float = 0.15,
    ):
        self.iv_rank_weight = iv_rank_weight
        self.put_yield_weight = put_yield_weight
        self.financial_weight = financial_weight
        self.liquidity_weight = liquidity_weight

    def score(self, stock_data: dict) -> float:
        """Calculate a composite score (0-100) for a stock."""
        iv_score = self._iv_score(stock_data)
        yield_score = self._yield_score(stock_data)
        fin_score = self._financial_score(stock_data)
        liq_score = self._liquidity_score(stock_data)

        total = (
            iv_score * self.iv_rank_weight
            + yield_score * self.put_yield_weight
            + fin_score * self.financial_weight
            + liq_score * self.liquidity_weight
        )
        return round(min(100, max(0, total)), 1)

    def _iv_score(self, data: dict) -> float:
        """IV Rank 0-100 maps directly to score 0-100."""
        iv_rank = data.get("iv_rank")
        if iv_rank is None:
            return 50
        return min(100, max(0, iv_rank))

    def _yield_score(self, data: dict) -> float:
        """Put premium yield: 0% -> 0, 1% -> 50, 2%+ -> 100."""
        put_yield = data.get("put_premium_yield", 0)
        return min(100, max(0, put_yield * 50))

    def _financial_score(self, data: dict) -> float:
        """Score based on PE (lower is better for value) and margin."""
        pe = data.get("pe_ratio")
        margin = data.get("profit_margin", 0)

        pe_score = 50
        if pe is not None and pe > 0:
            if pe < 15:
                pe_score = 90
            elif pe < 25:
                pe_score = 70
            elif pe < 35:
                pe_score = 50
            else:
                pe_score = 30

        margin_score = min(100, max(0, (margin or 0) * 3))
        return pe_score * 0.6 + margin_score * 0.4

    def _liquidity_score(self, data: dict) -> float:
        """Score based on option and stock volume."""
        opt_vol = data.get("option_volume", 0)
        stk_vol = data.get("volume", 0)

        opt_score = min(100, opt_vol / 50)  # 5000 vol -> 100
        stk_score = min(100, stk_vol / 50000)  # 5M vol -> 100
        return opt_score * 0.6 + stk_score * 0.4
