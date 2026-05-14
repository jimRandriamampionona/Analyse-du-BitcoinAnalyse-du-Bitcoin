from __future__ import annotations

from pathlib import Path
from typing import Mapping

import pandas as pd


def ensure_directories(*directories: Path) -> None:
    """Crée les dossiers nécessaires aux exports du dashboard."""
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def load_css(css_path: Path) -> str:
    """Lit le fichier CSS si disponible, sinon retourne une chaîne vide."""
    if not css_path.exists():
        return ""
    return css_path.read_text(encoding="utf-8")


def save_plotly_figures(figures: Mapping[str, object], output_dir: Path) -> dict[str, Path]:
    """Sauvegarde les figures Plotly en HTML autonome."""
    ensure_directories(output_dir)
    saved_paths: dict[str, Path] = {}
    for name, figure in figures.items():
        # Les noms sont normalisés pour produire des fichiers compatibles Windows
        # et faciles à retrouver dans le dossier outputs.
        safe_name = name.lower().replace(" ", "_").replace("/", "_")
        output_path = output_dir / f"{safe_name}.html"
        figure.write_html(output_path, include_plotlyjs="cdn", full_html=True)
        saved_paths[name] = output_path
    return saved_paths


def save_dataframe(df: pd.DataFrame, output_path: Path) -> Path:
    """Exporte un DataFrame en CSV UTF-8."""
    ensure_directories(output_path.parent)
    df.to_csv(output_path, index=False, encoding="utf-8")
    return output_path


def save_text_report(content: str, output_path: Path) -> Path:
    """Exporte un rapport texte ou Markdown en UTF-8."""
    ensure_directories(output_path.parent)
    output_path.write_text(content, encoding="utf-8")
    return output_path


def format_currency(value: float | int | None) -> str:
    """Formate une valeur numérique en montant USD."""
    if value is None or pd.isna(value):
        return "N/A"
    return f"${value:,.2f}"


def format_percent(value: float | int | None) -> str:
    """Formate un ratio décimal en pourcentage."""
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value * 100:,.2f}%"


def format_number(value: float | int | None) -> str:
    """Formate les grands volumes en K, M ou B pour les cartes KPI."""
    if value is None or pd.isna(value):
        return "N/A"

    # Les suffixes améliorent la lisibilité des volumes de transaction.
    abs_value = abs(float(value))
    if abs_value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    if abs_value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if abs_value >= 1_000:
        return f"{value / 1_000:.2f}K"
    return f"{value:,.0f}"


def quality_badge(value: str) -> str:
    """Retourne un badge HTML sobre pour afficher l'état du CSV."""
    return f"<span class='quality-badge'>{value}</span>"
