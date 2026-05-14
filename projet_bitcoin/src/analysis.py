from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class TrendInsight:
    title: str
    status: str
    description: str


def compute_kpis(df: pd.DataFrame) -> dict[str, object]:
    if df.empty:
        return {}

    first_close = float(df["Close"].iloc[0])
    latest_close = float(df["Close"].iloc[-1])
    period_return = (latest_close / first_close) - 1 if first_close else np.nan
    annualized_volatility = float(df["Daily_Return"].std() * np.sqrt(365))
    max_drawdown = float(df["Drawdown"].min())
    average_volume = float(df["Volume"].mean())

    best_idx = df["Daily_Return"].idxmax()
    worst_idx = df["Daily_Return"].idxmin()

    return {
        "first_close": first_close,
        "latest_close": latest_close,
        "period_return": period_return,
        "annualized_volatility": annualized_volatility,
        "max_drawdown": max_drawdown,
        "average_volume": average_volume,
        "best_day": df.loc[best_idx, "Date"],
        "best_day_return": float(df.loc[best_idx, "Daily_Return"]),
        "worst_day": df.loc[worst_idx, "Date"],
        "worst_day_return": float(df.loc[worst_idx, "Daily_Return"]),
        "observations": int(len(df)),
    }


def descriptive_statistics(df: pd.DataFrame) -> pd.DataFrame:
    columns = ["Close", "Volume", "Daily_Return", "Volatility_30D", "Price_Range", "Drawdown"]
    available_columns = [column for column in columns if column in df.columns]
    stats = df[available_columns].agg(["count", "mean", "median", "std", "min", "max"]).T
    stats = stats.reset_index().rename(columns={"index": "Variable"})
    return stats


def analyze_trends(df: pd.DataFrame, sma_column: str, ema_column: str) -> dict[str, object]:
    required = ["Close", "Daily_Return", "Volatility_30D", sma_column, ema_column]
    valid = df.dropna(subset=[column for column in required if column in df.columns]).copy()

    if valid.empty:
        return {
            "label": "Données insuffisantes",
            "score": 0,
            "insights": [
                TrendInsight(
                    "Fenêtre de calcul",
                    "À compléter",
                    "La période sélectionnée est trop courte pour calculer correctement les centres mobiles.",
                )
            ],
            "conclusion": "Veuillez sélectionner une période plus longue pour produire une analyse fiable.",
        }

    latest = valid.iloc[-1]
    close = float(latest["Close"])
    sma = float(latest[sma_column])
    ema = float(latest[ema_column])

    lookback = min(30, len(valid) - 1)
    close_momentum = (close / float(valid["Close"].iloc[-lookback - 1])) - 1 if lookback else 0
    sma_slope = (sma / float(valid[sma_column].iloc[-lookback - 1])) - 1 if lookback else 0
    ema_slope = (ema / float(valid[ema_column].iloc[-lookback - 1])) - 1 if lookback else 0

    score = 0
    score += 1 if close > sma else -1
    score += 1 if close > ema else -1
    score += 1 if ema > sma else -1
    score += 1 if close_momentum > 0 else -1
    score += 1 if ema_slope > sma_slope else 0

    if score >= 3:
        label = "Tendance haussière"
        trend_text = "Le prix reste au-dessus des deux centres mobiles; l'EMA confirme une réaction rapide du marché."
    elif score <= -3:
        label = "Tendance baissière"
        trend_text = "Le prix évolue sous les centres mobiles; le lissage confirme une pression vendeuse dominante."
    else:
        label = "Tendance mixte"
        trend_text = "Les signaux sont partagés; la méthode des centres mobiles indique une zone de transition."

    volatility_latest = float(valid["Volatility_30D"].iloc[-1])
    volatility_median = float(valid["Volatility_30D"].median())
    if volatility_latest > volatility_median * 1.25:
        volatility_status = "Élevée"
        volatility_text = "La volatilité récente dépasse nettement sa médiane, ce qui augmente le risque de retournement court terme."
    elif volatility_latest < volatility_median * 0.80:
        volatility_status = "Modérée"
        volatility_text = "La volatilité récente est inférieure à sa médiane, ce qui donne un signal de marché plus stabilisé."
    else:
        volatility_status = "Normale"
        volatility_text = "La volatilité récente reste proche de son régime médian."

    close_vol = valid["Close"].pct_change().std()
    sma_vol = valid[sma_column].pct_change().std()
    ema_vol = valid[ema_column].pct_change().std()
    sma_reduction = 1 - (sma_vol / close_vol) if close_vol else np.nan
    ema_reduction = 1 - (ema_vol / close_vol) if close_vol else np.nan

    sma_gap = ((valid["Close"] - valid[sma_column]).abs() / valid["Close"]).mean()
    ema_gap = ((valid["Close"] - valid[ema_column]).abs() / valid["Close"]).mean()
    responsive = "EMA" if ema_gap < sma_gap else "SMA"

    insights = [
        TrendInsight("Signal global", label, trend_text),
        TrendInsight(
            "Effet du lissage",
            "Net",
            f"La SMA réduit la variabilité quotidienne d'environ {sma_reduction * 100:.1f}%, contre {ema_reduction * 100:.1f}% pour l'EMA.",
        ),
        TrendInsight(
            "Comparaison SMA vs EMA",
            responsive,
            f"La {responsive} est la plus proche du prix observé sur la période sélectionnée, donc elle réagit mieux aux mouvements récents.",
        ),
        TrendInsight("Volatilité", volatility_status, volatility_text),
    ]

    conclusion = (
        f"Conclusion automatique: la méthode des centres mobiles indique une {label.lower()} "
        f"sur la période étudiée. La SMA fournit une lecture plus lissée de la tendance de fond, "
        f"tandis que l'EMA réagit plus vite aux changements de prix. Cette complémentarité permet "
        f"de distinguer le bruit quotidien du mouvement directionnel du Bitcoin."
    )

    return {
        "label": label,
        "score": score,
        "close_momentum": close_momentum,
        "sma_slope": sma_slope,
        "ema_slope": ema_slope,
        "sma_reduction": sma_reduction,
        "ema_reduction": ema_reduction,
        "sma_gap": sma_gap,
        "ema_gap": ema_gap,
        "insights": insights,
        "conclusion": conclusion,
    }


def build_markdown_report(
    df: pd.DataFrame,
    kpis: dict[str, object],
    trend_analysis: dict[str, object],
    sma_column: str,
    ema_column: str,
) -> str:
    start_date = df["Date"].min().strftime("%d/%m/%Y")
    end_date = df["Date"].max().strftime("%d/%m/%Y")
    insights = trend_analysis.get("insights", [])
    insight_lines = "\n".join(
        f"- **{item.title} ({item.status})**: {item.description}" for item in insights
    )

    return f"""# Rapport automatique - Analyse du Bitcoin par la méthode des centres mobiles

## Période analysée
- Début: {start_date}
- Fin: {end_date}
- Nombre d'observations: {kpis.get("observations", 0)}

## Formules utilisées
- SMA: moyenne arithmétique des n valeurs précédentes.
- EMA: EMA_t = alpha * x_t + (1 - alpha) * EMA_(t-1).

## Indicateurs calculés
- Colonne SMA: `{sma_column}`
- Colonne EMA: `{ema_column}`
- Rendements journaliers, volatilité annualisée, drawdown et volume moyen.

## Résultats clés
- Prix final: {kpis.get("latest_close", np.nan):,.2f} USD
- Rendement sur la période: {kpis.get("period_return", np.nan) * 100:,.2f}%
- Volatilité annualisée: {kpis.get("annualized_volatility", np.nan) * 100:,.2f}%
- Drawdown maximal: {kpis.get("max_drawdown", np.nan) * 100:,.2f}%

## Analyse automatique
{insight_lines}

## Conclusion
{trend_analysis.get("conclusion", "Analyse non disponible.")}
"""
