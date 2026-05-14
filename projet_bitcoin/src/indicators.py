from __future__ import annotations

import pandas as pd


def calculate_sma(series: pd.Series, window: int = 30) -> pd.Series:
    """Calcule la moyenne mobile simple sur une fenêtre fixe.

    Formule utilisée:
        SMA_t = (x_t + x_(t-1) + ... + x_(t-n+1)) / n

    Interprétation:
        La SMA donne le même poids aux n dernières observations. Elle réduit le
        bruit de court terme et met en évidence la tendance moyenne du Bitcoin.
    """
    if window < 2:
        raise ValueError("La fenêtre SMA doit être supérieure ou égale à 2.")

    # min_periods=window évite d'afficher une SMA avant d'avoir assez de données.
    return series.rolling(window=window, min_periods=window).mean()


def calculate_ema(series: pd.Series, span: int = 30) -> pd.Series:
    """Calcule la moyenne mobile exponentielle.

    Formule utilisée:
        EMA_t = alpha * x_t + (1 - alpha) * EMA_(t-1)
        alpha = 2 / (span + 1)

    Interprétation:
        L'EMA attribue plus de poids aux valeurs récentes. Elle réagit donc plus
        rapidement aux changements de tendance que la SMA.
    """
    if span < 2:
        raise ValueError("La période EMA doit être supérieure ou égale à 2.")

    # adjust=False applique la définition récursive classique de l'EMA.
    # min_periods=span limite les signaux prématurés au début de la série.
    return series.ewm(span=span, adjust=False, min_periods=span).mean()


def add_moving_averages(
    df: pd.DataFrame,
    sma_window: int = 30,
    ema_span: int = 30,
    price_column: str = "Close",
) -> tuple[pd.DataFrame, str, str]:
    """Ajoute les centres mobiles et les signaux de tendance au DataFrame.

    Les colonnes ajoutées servent à comparer trois informations:
    prix original, SMA et EMA. Cette comparaison est le coeur de la méthode des
    centres mobiles utilisée dans le dashboard.
    """
    if price_column not in df.columns:
        raise ValueError(f"La colonne {price_column} est absente du jeu de données.")

    data = df.copy()
    sma_column = f"SMA_{sma_window}"
    ema_column = f"EMA_{ema_span}"

    # Calcul de la SMA: chaque observation de la fenêtre a le même poids.
    data[sma_column] = calculate_sma(data[price_column], window=sma_window)

    # Calcul de l'EMA: les observations récentes sont pondérées plus fortement.
    data[ema_column] = calculate_ema(data[price_column], span=ema_span)

    # Écart entre EMA et SMA. Un écart positif indique souvent que la tendance
    # récente accélère plus vite que la tendance moyenne de la fenêtre.
    data["SMA_EMA_Spread"] = data[ema_column] - data[sma_column]

    # Distances relatives entre le prix observé et les centres mobiles.
    data["Close_vs_SMA"] = (data[price_column] - data[sma_column]) / data[sma_column]
    data["Close_vs_EMA"] = (data[price_column] - data[ema_column]) / data[ema_column]

    # Signal simple et interprétable pour la soutenance:
    # prix au-dessus des deux moyennes = signal haussier,
    # prix sous les deux moyennes = signal baissier.
    data["Signal"] = "Neutre"
    data.loc[(data[price_column] > data[sma_column]) & (data[price_column] > data[ema_column]), "Signal"] = "Haussier"
    data.loc[(data[price_column] < data[sma_column]) & (data[price_column] < data[ema_column]), "Signal"] = "Baissier"

    return data, sma_column, ema_column


def moving_average_formula_text() -> dict[str, str]:
    """Retourne les formules affichées dans l'interface Streamlit."""
    return {
        "SMA": "SMA_t = (x_t + x_(t-1) + ... + x_(t-n+1)) / n",
        "EMA": "EMA_t = alpha * x_t + (1 - alpha) * EMA_(t-1), avec alpha = 2 / (n + 1)",
    }
