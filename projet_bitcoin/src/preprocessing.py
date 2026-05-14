from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Volume"]
OPTIONAL_COLUMNS = ["Adj Close"]

COLUMN_ALIASES = {
    "date": "Date",
    "open": "Open",
    "high": "High",
    "low": "Low",
    "close": "Close",
    "adj close": "Adj Close",
    "adj_close": "Adj Close",
    "adjusted close": "Adj Close",
    "volume": "Volume",
}


def load_csv(csv_path: str | Path) -> pd.DataFrame:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Le fichier {path.name} est introuvable dans le projet.")

    df = pd.read_csv(path)
    if df.empty:
        raise ValueError("Le fichier CSV est vide.")
    return df


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed_columns = {}
    for column in df.columns:
        clean_column = str(column).strip()
        alias_key = clean_column.lower().replace("-", " ").replace("_", " ")
        renamed_columns[column] = COLUMN_ALIASES.get(alias_key, clean_column)
    return df.rename(columns=renamed_columns)


def validate_schema(df: pd.DataFrame) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        missing_columns = ", ".join(missing)
        raise ValueError(f"Colonnes obligatoires manquantes dans le CSV: {missing_columns}")


def clean_bitcoin_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    data = standardize_columns(df.copy())
    validate_schema(data)

    rows_before = len(data)
    missing_before = data.isna().sum().to_dict()

    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")

    numeric_columns = [column for column in REQUIRED_COLUMNS + OPTIONAL_COLUMNS if column in data.columns]
    numeric_columns = [column for column in numeric_columns if column != "Date"]

    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    invalid_dates = int(data["Date"].isna().sum())
    data = data.dropna(subset=["Date", "Close"])

    duplicate_dates = int(data.duplicated(subset=["Date"]).sum())
    data = data.drop_duplicates(subset=["Date"], keep="last").sort_values("Date")

    data[numeric_columns] = data[numeric_columns].replace([np.inf, -np.inf], np.nan)

    price_columns = [column for column in ["Open", "High", "Low", "Close", "Adj Close"] if column in data.columns]
    for column in price_columns:
        data.loc[data[column] <= 0, column] = np.nan

    data[numeric_columns] = data[numeric_columns].interpolate(method="linear", limit_direction="both")
    data[numeric_columns] = data[numeric_columns].ffill().bfill()
    data["Volume"] = data["Volume"].fillna(0).clip(lower=0)

    data = data.dropna(subset=["Close"]).reset_index(drop=True)
    data = add_engineered_features(data)

    report = {
        "rows_before": rows_before,
        "rows_after": len(data),
        "columns": list(data.columns),
        "missing_before": missing_before,
        "missing_after": data.isna().sum().to_dict(),
        "invalid_dates_removed": invalid_dates,
        "duplicate_dates_removed": duplicate_dates,
        "start_date": data["Date"].min(),
        "end_date": data["Date"].max(),
    }
    return data, report


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    data["Year"] = data["Date"].dt.year
    data["Month"] = data["Date"].dt.to_period("M").astype(str)
    data["Daily_Return"] = data["Close"].pct_change().replace([np.inf, -np.inf], np.nan).fillna(0)
    data["Log_Return"] = np.log(data["Close"] / data["Close"].shift(1)).replace([np.inf, -np.inf], np.nan).fillna(0)
    data["Price_Range"] = data["High"] - data["Low"]
    data["Range_Pct"] = (data["Price_Range"] / data["Close"]).replace([np.inf, -np.inf], np.nan)
    data["Volatility_30D"] = data["Daily_Return"].rolling(window=30, min_periods=10).std() * np.sqrt(365)
    data["Volume_MA_30"] = data["Volume"].rolling(window=30, min_periods=1).mean()

    cumulative_max = data["Close"].cummax()
    data["Drawdown"] = (data["Close"] / cumulative_max) - 1
    return data
