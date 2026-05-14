from __future__ import annotations

import pandas as pd


def calculate_sma(series: pd.Series, window: int = 30) -> pd.Series:
    if window < 2:
        raise ValueError("La fenêtre SMA doit être supérieure ou égale à 2.")
    return series.rolling(window=window, min_periods=window).mean()


def calculate_ema(series: pd.Series, span: int = 30) -> pd.Series:
    if span < 2:
        raise ValueError("La période EMA doit être supérieure ou égale à 2.")
    return series.ewm(span=span, adjust=False, min_periods=span).mean()


def add_moving_averages(
    df: pd.DataFrame,
    sma_window: int = 30,
    ema_span: int = 30,
    price_column: str = "Close",
) -> tuple[pd.DataFrame, str, str]:
    if price_column not in df.columns:
        raise ValueError(f"La colonne {price_column} est absente du jeu de données.")

    data = df.copy()
    sma_column = f"SMA_{sma_window}"
    ema_column = f"EMA_{ema_span}"

    data[sma_column] = calculate_sma(data[price_column], window=sma_window)
    data[ema_column] = calculate_ema(data[price_column], span=ema_span)

    data["SMA_EMA_Spread"] = data[ema_column] - data[sma_column]
    data["Close_vs_SMA"] = (data[price_column] - data[sma_column]) / data[sma_column]
    data["Close_vs_EMA"] = (data[price_column] - data[ema_column]) / data[ema_column]
    data["Signal"] = "Neutre"
    data.loc[(data[price_column] > data[sma_column]) & (data[price_column] > data[ema_column]), "Signal"] = "Haussier"
    data.loc[(data[price_column] < data[sma_column]) & (data[price_column] < data[ema_column]), "Signal"] = "Baissier"

    return data, sma_column, ema_column


def moving_average_formula_text() -> dict[str, str]:
    return {
        "SMA": "SMA_t = moyenne arithmétique des n valeurs précédentes",
        "EMA": "EMA_t = alpha * x_t + (1 - alpha) * EMA_(t-1)",
    }
