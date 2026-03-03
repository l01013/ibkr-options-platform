"""Reusable chart components for Plotly Dash."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_candlestick_chart(
    bars: list[dict],
    symbol: str = "",
    ma_periods: list[int] | None = None,
    show_volume: bool = True,
) -> go.Figure:
    """Create a candlestick chart with optional moving averages and volume."""
    if not bars:
        fig = go.Figure()
        fig.update_layout(
            title="No data available",
            template="plotly_dark",
        )
        return fig

    import pandas as pd
    df = pd.DataFrame(bars)
    df["date"] = pd.to_datetime(df["date"])

    row_heights = [0.7, 0.3] if show_volume else [1.0]
    rows = 2 if show_volume else 1

    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=row_heights,
    )

    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df["date"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="Price",
            increasing_line_color="#26a69a",
            decreasing_line_color="#ef5350",
        ),
        row=1,
        col=1,
    )

    # Moving averages
    if ma_periods is None:
        ma_periods = [20, 50, 200]

    colors = ["#FFA726", "#42A5F5", "#AB47BC", "#66BB6A"]
    for i, period in enumerate(ma_periods):
        if len(df) >= period:
            ma = df["close"].rolling(window=period).mean()
            fig.add_trace(
                go.Scatter(
                    x=df["date"],
                    y=ma,
                    name=f"MA{period}",
                    line=dict(color=colors[i % len(colors)], width=1),
                ),
                row=1,
                col=1,
            )

    # Volume
    if show_volume and "volume" in df.columns:
        colors_vol = [
            "#26a69a" if row["close"] >= row["open"] else "#ef5350"
            for _, row in df.iterrows()
        ]
        fig.add_trace(
            go.Bar(
                x=df["date"],
                y=df["volume"],
                name="Volume",
                marker_color=colors_vol,
                opacity=0.5,
            ),
            row=2,
            col=1,
        )

    fig.update_layout(
        title=f"{symbol} Price Chart" if symbol else "Price Chart",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=600,
        margin=dict(l=50, r=50, t=50, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        showlegend=True,
    )
    fig.update_xaxes(type="date")

    return fig


def create_pnl_chart(
    dates: list,
    pnl_values: list[float],
    benchmark_values: list[float] | None = None,
    initial_capital: float | None = None,
    title: str = "P&L Curve",
) -> go.Figure:
    """Create a P&L curve chart with optional benchmark comparison and percentage display."""
    fig = go.Figure()

    # Add P&L in dollars (primary trace)
    strategy_trace = go.Scatter(
        x=dates,
        y=pnl_values,
        name="Strategy P&L ($)",
        line=dict(color="#26a69a", width=2),
        fill="tozeroy",
        fillcolor="rgba(38, 166, 154, 0.1)",
    )
    
    # Add percentage trace if initial capital is provided
    if initial_capital and initial_capital > 0:
        percentage_values = [pnl / initial_capital * 100 for pnl in pnl_values]
        percentage_trace = go.Scatter(
            x=dates,
            y=percentage_values,
            name="Strategy Return (%)",
            line=dict(color="#42A5F5", width=2, dash="dot"),
            yaxis="y2",
        )
        fig.add_trace(percentage_trace)
    
    fig.add_trace(strategy_trace)

    if benchmark_values:
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=benchmark_values,
                name="Benchmark (B&H)",
                line=dict(color="#FFA726", width=1.5, dash="dash"),
            )
        )

    # Update layout with dual y-axes if percentage is shown
    layout_updates = dict(
        title=title,
        template="plotly_dark",
        height=400,
        margin=dict(l=50, r=50, t=50, b=30),
        yaxis_title="P&L ($)",
        xaxis_title="Date",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    
    # Add second y-axis for percentage if needed
    if initial_capital and initial_capital > 0:
        layout_updates["yaxis2"] = dict(
            title="Return (%)",
            overlaying="y",
            side="right",
            gridcolor="rgba(255,255,255,0.1)",
        )
    
    fig.update_layout(**layout_updates)
    return fig


def create_monthly_heatmap(monthly_returns: dict) -> go.Figure:
    """Create monthly returns heatmap.

    monthly_returns: {(year, month): return_pct, ...}
    """
    import pandas as pd

    if not monthly_returns:
        fig = go.Figure()
        fig.update_layout(title="No data", template="plotly_dark")
        return fig

    df = pd.DataFrame(
        [(y, m, v) for (y, m), v in monthly_returns.items()],
        columns=["year", "month", "return_pct"],
    )
    pivot = df.pivot(index="year", columns="month", values="return_pct")
    pivot = pivot.reindex(columns=range(1, 13))

    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    fig = go.Figure(
        go.Heatmap(
            z=pivot.values,
            x=month_labels,
            y=[str(y) for y in pivot.index],
            colorscale="RdYlGn",
            zmid=0,
            text=pivot.values.round(1),
            texttemplate="%{text}%",
            textfont={"size": 10},
            colorbar_title="Return %",
        )
    )
    fig.update_layout(
        title="Monthly Returns",
        template="plotly_dark",
        height=300,
        margin=dict(l=50, r=50, t=50, b=30),
    )
    return fig
