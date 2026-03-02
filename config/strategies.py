"""Default parameters for options strategies."""

STRATEGY_DEFAULTS = {
    "sell_put": {
        "dte_min": 21,
        "dte_max": 45,
        "delta_target": -0.30,
        "profit_target_pct": 50.0,
        "stop_loss_pct": 200.0,
        "roll_dte_threshold": 7,
        "max_positions": 5,
    },
    "covered_call": {
        "dte_min": 21,
        "dte_max": 45,
        "delta_target": 0.30,
        "profit_target_pct": 50.0,
        "stop_loss_pct": 200.0,
        "roll_dte_threshold": 7,
    },
    "iron_condor": {
        "dte_min": 30,
        "dte_max": 60,
        "put_delta_target": -0.16,
        "call_delta_target": 0.16,
        "wing_width": 5.0,
        "profit_target_pct": 50.0,
        "stop_loss_pct": 200.0,
    },
    "bull_put_spread": {
        "dte_min": 21,
        "dte_max": 45,
        "short_delta_target": -0.30,
        "spread_width": 5.0,
        "profit_target_pct": 50.0,
        "stop_loss_pct": 200.0,
    },
    "bear_call_spread": {
        "dte_min": 21,
        "dte_max": 45,
        "short_delta_target": 0.30,
        "spread_width": 5.0,
        "profit_target_pct": 50.0,
        "stop_loss_pct": 200.0,
    },
    "straddle": {
        "dte_min": 30,
        "dte_max": 60,
        "profit_target_pct": 25.0,
        "stop_loss_pct": 100.0,
    },
    "strangle": {
        "dte_min": 30,
        "dte_max": 60,
        "put_delta_target": -0.20,
        "call_delta_target": 0.20,
        "profit_target_pct": 50.0,
        "stop_loss_pct": 200.0,
    },
}

# Default screening criteria
SCREENING_DEFAULTS = {
    "pe_min": 0,
    "pe_max": 50,
    "market_cap_min": 2_000_000_000,  # $2B
    "market_cap_max": None,
    "iv_rank_min": 30,
    "iv_rank_max": 100,
    "min_option_volume": 100,
    "min_stock_volume": 500_000,
    "exchanges": ["NYSE", "NASDAQ"],
}
