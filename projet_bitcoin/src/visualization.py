from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


COLORS = {
    "background": "#05070f",
    "panel": "#0b1020",
    "grid": "rgba(148, 163, 184, 0.14)",
    "text": "#dbeafe",
    "muted": "#94a3b8",
    "cyan": "#22d3ee",
    "blue": "#3b82f6",
    "violet": "#8b5cf6",
    "green": "#22c55e",
    "red": "#fb7185",
    "amber": "#f59e0b",
}


def _apply_dark_layout(fig: go.Figure, title: str, yaxis_title: str = "", height: int = 520) -> go.Figure:
    fig.update_layout(
        title={"text": title, "x": 0.02, "xanchor": "left", "font": {"size": 22, "color": COLORS["text"]}},
        height=height,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(5,7,15,0.72)",
        font={"family": "Inter, Segoe UI, sans-serif", "color": COLORS["text"]},
        margin={"l": 28, "r": 24, "t": 72, "b": 36},
        hovermode="x unified",
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "bgcolor": "rgba(5,7,15,0.45)",
        },
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(title=yaxis_title, gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"])
    return fig


def create_price_chart(df: pd.DataFrame, sma_column: str, ema_column: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Close"],
            mode="lines",
            name="Prix de clôture",
            line={"color": COLORS["cyan"], "width": 2.4},
            hovertemplate="%{x|%d/%m/%Y}<br>Close: $%{y:,.2f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df[sma_column],
            mode="lines",
            name=sma_column,
            line={"color": COLORS["violet"], "width": 2.1},
            hovertemplate="%{x|%d/%m/%Y}<br>SMA: $%{y:,.2f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df[ema_column],
            mode="lines",
            name=ema_column,
            line={"color": COLORS["blue"], "width": 2.1},
            hovertemplate="%{x|%d/%m/%Y}<br>EMA: $%{y:,.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis={
            "rangeselector": {
                "buttons": [
                    {"count": 1, "label": "1M", "step": "month", "stepmode": "backward"},
                    {"count": 6, "label": "6M", "step": "month", "stepmode": "backward"},
                    {"count": 1, "label": "1A", "step": "year", "stepmode": "backward"},
                    {"step": "all", "label": "Tout"},
                ],
                "bgcolor": "rgba(15,23,42,0.85)",
                "activecolor": COLORS["blue"],
                "font": {"color": COLORS["text"]},
            },
            "rangeslider": {"visible": True, "thickness": 0.06},
        }
    )
    return _apply_dark_layout(fig, "Courbe du prix du Bitcoin avec SMA et EMA", "Prix USD")


def create_sma_focus_chart(df: pd.DataFrame, sma_column: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], name="Prix original", line={"color": COLORS["cyan"], "width": 1.7}))
    fig.add_trace(go.Scatter(x=df["Date"], y=df[sma_column], name=sma_column, line={"color": COLORS["violet"], "width": 3}))
    return _apply_dark_layout(fig, f"SMA - centre mobile simple ({sma_column})", "Prix USD", height=460)


def create_ema_focus_chart(df: pd.DataFrame, ema_column: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], name="Prix original", line={"color": COLORS["cyan"], "width": 1.7}))
    fig.add_trace(go.Scatter(x=df["Date"], y=df[ema_column], name=ema_column, line={"color": COLORS["blue"], "width": 3}))
    return _apply_dark_layout(fig, f"EMA - centre mobile exponentiel ({ema_column})", "Prix USD", height=460)


def create_sma_ema_comparison(df: pd.DataFrame, sma_column: str, ema_column: str) -> go.Figure:
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.72, 0.28],
        subplot_titles=("Comparaison des centres mobiles", "Écart EMA - SMA"),
    )
    fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], name="Close", line={"color": COLORS["cyan"], "width": 1.5}), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df[sma_column], name=sma_column, line={"color": COLORS["violet"], "width": 2.5}), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df[ema_column], name=ema_column, line={"color": COLORS["blue"], "width": 2.5}), row=1, col=1)
    fig.add_trace(
        go.Bar(
            x=df["Date"],
            y=df["SMA_EMA_Spread"],
            name="Spread EMA-SMA",
            marker_color=df["SMA_EMA_Spread"].apply(lambda value: COLORS["green"] if value >= 0 else COLORS["red"]),
            opacity=0.75,
        ),
        row=2,
        col=1,
    )
    return _apply_dark_layout(fig, "Comparaison SMA vs EMA", "Prix USD", height=620)


def create_volume_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["Date"],
            y=df["Volume"],
            name="Volume",
            marker_color="rgba(34, 211, 238, 0.45)",
            hovertemplate="%{x|%d/%m/%Y}<br>Volume: %{y:,.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Volume_MA_30"],
            name="Volume moyen 30J",
            line={"color": COLORS["amber"], "width": 2.4},
        )
    )
    return _apply_dark_layout(fig, "Volume des transactions", "Volume", height=460)


def create_volatility_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Volatility_30D"],
            name="Volatilité annualisée 30J",
            mode="lines",
            fill="tozeroy",
            line={"color": COLORS["red"], "width": 2.2},
            fillcolor="rgba(251, 113, 133, 0.18)",
        )
    )
    return _apply_dark_layout(fig, "Volatilité du Bitcoin", "Volatilité", height=440)


def create_candlestick_chart(df: pd.DataFrame, sma_column: str, ema_column: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Candlestick(
            x=df["Date"],
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="OHLC",
            increasing_line_color=COLORS["green"],
            decreasing_line_color=COLORS["red"],
        )
    )
    fig.add_trace(go.Scatter(x=df["Date"], y=df[sma_column], name=sma_column, line={"color": COLORS["violet"], "width": 1.8}))
    fig.add_trace(go.Scatter(x=df["Date"], y=df[ema_column], name=ema_column, line={"color": COLORS["blue"], "width": 1.8}))
    return _apply_dark_layout(fig, "Lecture financière OHLC avec centres mobiles", "Prix USD", height=560)
