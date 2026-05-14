from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


# Colonnes minimales attendues pour un fichier de prix type Yahoo Finance.
REQUIRED_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Volume"]
OPTIONAL_COLUMNS = ["Adj Close"]

# Dictionnaire de normalisation pour accepter des variantes courantes de noms.
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
    """Charge le CSV local et vérifie qu'il contient des observations."""
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Le fichier {path.name} est introuvable dans le projet.")

    df = pd.read_csv(path)
    if df.empty:
        raise ValueError("Le fichier CSV est vide.")
    return df


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Uniformise les noms de colonnes avant la validation du schéma."""
    renamed_columns = {}
    for column in df.columns:
        clean_column = str(column).strip()

        # Les séparateurs et la casse sont harmonisés pour reconnaître les alias.
        alias_key = clean_column.lower().replace("-", " ").replace("_", " ")
        renamed_columns[column] = COLUMN_ALIASES.get(alias_key, clean_column)
    return df.rename(columns=renamed_columns)


def validate_schema(df: pd.DataFrame) -> None:
    """Vérifie la présence des colonnes obligatoires du modèle financier."""
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        missing_columns = ", ".join(missing)
        raise ValueError(f"Colonnes obligatoires manquantes dans le CSV: {missing_columns}")


def clean_bitcoin_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Nettoie et enrichit les données Bitcoin avant l'analyse."""
    data = standardize_columns(df.copy())
    validate_schema(data)

    # Ces informations alimentent le bloc de qualité affiché dans la sidebar.
    rows_before = len(data)
    missing_before = data.isna().sum().to_dict()

    # Conversion robuste des dates: les valeurs illisibles deviennent NaT.
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")

    numeric_columns = [column for column in REQUIRED_COLUMNS + OPTIONAL_COLUMNS if column in data.columns]
    numeric_columns = [column for column in numeric_columns if column != "Date"]

    # Conversion des colonnes financières en numérique pour éviter les erreurs
    # de calcul sur des valeurs importées comme texte.
    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    # Les observations sans date ou sans prix de clôture ne peuvent pas être
    # utilisées pour une série temporelle fiable.
    invalid_dates = int(data["Date"].isna().sum())
    data = data.dropna(subset=["Date", "Close"])

    # Une seule observation par date est conservée, puis la série est triée.
    duplicate_dates = int(data.duplicated(subset=["Date"]).sum())
    data = data.drop_duplicates(subset=["Date"], keep="last").sort_values("Date")

    data[numeric_columns] = data[numeric_columns].replace([np.inf, -np.inf], np.nan)

    # Les prix négatifs ou nuls ne sont pas cohérents pour un actif financier.
    price_columns = [column for column in ["Open", "High", "Low", "Close", "Adj Close"] if column in data.columns]
    for column in price_columns:
        data.loc[data[column] <= 0, column] = np.nan

    # L'interpolation conserve la continuité de la série sans créer de données
    # aléatoires. Elle est complétée par ffill/bfill pour les bords.
    data[numeric_columns] = data[numeric_columns].interpolate(method="linear", limit_direction="both")
    data[numeric_columns] = data[numeric_columns].ffill().bfill()
    data["Volume"] = data["Volume"].fillna(0).clip(lower=0)

    # Les variables dérivées sont ajoutées après le nettoyage pour éviter des
    # calculs biaisés par des valeurs manquantes ou invalides.
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
    """Ajoute les variables nécessaires à l'analyse exploratoire et au risque."""
    data = df.copy()
    data["Year"] = data["Date"].dt.year
    data["Month"] = data["Date"].dt.to_period("M").astype(str)

    # Rendement simple: variation relative du prix de clôture entre deux jours.
    data["Daily_Return"] = data["Close"].pct_change().replace([np.inf, -np.inf], np.nan).fillna(0)

    # Rendement logarithmique: utile pour analyser les variations multiplicatives.
    data["Log_Return"] = np.log(data["Close"] / data["Close"].shift(1)).replace([np.inf, -np.inf], np.nan).fillna(0)
    data["Price_Range"] = data["High"] - data["Low"]
    data["Range_Pct"] = (data["Price_Range"] / data["Close"]).replace([np.inf, -np.inf], np.nan)

    # Volatilité annualisée sur 30 jours. La racine de 365 est utilisée car le
    # Bitcoin se négocie tous les jours de l'année.
    data["Volatility_30D"] = data["Daily_Return"].rolling(window=30, min_periods=10).std() * np.sqrt(365)
    data["Volume_MA_30"] = data["Volume"].rolling(window=30, min_periods=1).mean()

    # Drawdown: distance du prix actuel au plus haut historique observé jusque-là.
    cumulative_max = data["Close"].cummax()
    data["Drawdown"] = (data["Close"] / cumulative_max) - 1
    return data
