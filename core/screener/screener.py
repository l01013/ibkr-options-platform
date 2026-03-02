"""Main stock screener: orchestrates data fetching, filtering, and ranking."""

from core.ibkr.data_client import IBKRDataClient
from core.screener.criteria import ScreeningCriteria
from core.screener.filters import FinancialFilter, IVFilter, TechnicalFilter
from core.screener.ranker import ScreeningRanker
from utils.logger import setup_logger

logger = setup_logger("screener")


class StockScreener:
    """Screen stocks based on financial, options, and technical criteria."""

    def __init__(self, data_client: IBKRDataClient):
        self._client = data_client
        self._financial_filter = FinancialFilter()
        self._iv_filter = IVFilter()
        self._technical_filter = TechnicalFilter()
        self._ranker = ScreeningRanker()

    def run(
        self,
        symbols: list[str],
        criteria: ScreeningCriteria,
    ) -> list[dict]:
        """Run screener on a list of symbols. Returns ranked results."""
        results = []
        for symbol in symbols:
            try:
                stock_data = self._gather_data(symbol)
            except Exception as e:
                logger.warning("Failed to gather data for %s: %s", symbol, e)
                continue

            # Apply filters
            if not self._financial_filter.apply(stock_data, criteria):
                continue
            if not self._iv_filter.apply(stock_data, criteria):
                continue
            if not self._technical_filter.apply(stock_data, criteria):
                continue

            # Score
            score = self._ranker.score(stock_data)
            stock_data["score"] = score
            results.append(stock_data)

        # Sort by score descending
        results.sort(key=lambda x: x.get("score", 0), reverse=True)

        # Add rank
        for i, r in enumerate(results, 1):
            r["rank"] = i

        return results

    def _gather_data(self, symbol: str) -> dict:
        """Fetch and merge quote, fundamentals, and options data for screening."""
        # Real-time quote
        quote = self._client.get_realtime_quote(symbol)
        price = quote.get("last") or quote.get("close") or 0

        # Fundamentals
        fundamentals = self._client.get_fundamentals(symbol)

        # Options data: get nearest monthly expiry for IV/yield calc
        iv_rank = None
        atm_iv = None
        put_premium_yield = 0
        option_volume = 0

        try:
            params = self._client.get_option_chain_params(symbol)
            if params and params[0].get("expirations"):
                expirations = params[0]["expirations"]
                # Pick first expiry that's 21-45 DTE
                from datetime import date, datetime
                today = date.today()
                target_expiry = None
                for exp in expirations:
                    try:
                        exp_date = datetime.strptime(exp, "%Y%m%d").date()
                        dte = (exp_date - today).days
                        if 21 <= dte <= 60:
                            target_expiry = exp
                            break
                    except ValueError:
                        continue

                if target_expiry is None and expirations:
                    target_expiry = expirations[0]

                if target_expiry and price > 0:
                    # Get ATM options
                    strikes = params[0].get("strikes", [])
                    atm_strikes = sorted(strikes, key=lambda s: abs(s - price))[:3]

                    chain = self._client.get_option_chain(
                        symbol, target_expiry, strikes=atm_strikes, right="P"
                    )
                    if chain:
                        # ATM IV
                        atm_opt = min(chain, key=lambda c: abs(c["strike"] - price))
                        atm_iv = (atm_opt.get("impliedVol") or 0) * 100

                        # Put premium yield: ATM put mid / stock price * 100
                        bid = atm_opt.get("bid") or 0
                        ask = atm_opt.get("ask") or 0
                        mid = (bid + ask) / 2 if bid and ask else 0
                        put_premium_yield = (mid / price * 100) if price > 0 else 0

                        # Total option volume
                        option_volume = sum(c.get("volume") or 0 for c in chain)

                        # Rough IV rank (using current IV vs 52-week range from fundamentals)
                        if atm_iv and fundamentals.get("week52_high"):
                            iv_rank = min(100, max(0, atm_iv))  # simplified
        except Exception as e:
            logger.debug("Options data unavailable for %s: %s", symbol, e)

        return {
            "symbol": symbol,
            "price": price,
            "volume": quote.get("volume", 0),
            "pe_ratio": fundamentals.get("pe_ratio"),
            "market_cap": fundamentals.get("market_cap"),
            "market_cap_b": (fundamentals.get("market_cap") or 0) / 1e9 or None,
            "revenue": fundamentals.get("revenue"),
            "revenue_growth": fundamentals.get("revenue_growth"),
            "profit_margin": fundamentals.get("profit_margin"),
            "dividend_yield": fundamentals.get("dividend_yield"),
            "beta": fundamentals.get("beta"),
            "iv_rank": iv_rank,
            "atm_iv": atm_iv,
            "put_premium_yield": put_premium_yield,
            "option_volume": option_volume,
        }
