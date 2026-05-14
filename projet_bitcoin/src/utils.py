from __future__ import annotations

from pathlib import Path
from typing import Mapping

import pandas as pd


def ensure_directories(*directories: Path) -> None:
    """Create output directories required by the application."""
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def load_css(css_path: Path) -> str:
    if not css_path.exists():
        return ""
    return css_path.read_text(encoding="utf-8")


def save_plotly_figures(figures: Mapping[str, object], output_dir: Path) -> dict[str, Path]:
    ensure_directories(output_dir)
    saved_paths: dict[str, Path] = {}
    for name, figure in figures.items():
        safe_name = name.lower().replace(" ", "_").replace("/", "_")
        output_path = output_dir / f"{safe_name}.html"
        figure.write_html(output_path, include_plotlyjs="cdn", full_html=True)
        saved_paths[name] = output_path
    return saved_paths


def save_dataframe(df: pd.DataFrame, output_path: Path) -> Path:
    ensure_directories(output_path.parent)
    df.to_csv(output_path, index=False, encoding="utf-8")
    return output_path


def save_text_report(content: str, output_path: Path) -> Path:
    ensure_directories(output_path.parent)
    output_path.write_text(content, encoding="utf-8")
    return output_path


def format_currency(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"${value:,.2f}"


def format_percent(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value * 100:,.2f}%"


def format_number(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    abs_value = abs(float(value))
    if abs_value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    if abs_value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if abs_value >= 1_000:
        return f"{value / 1_000:.2f}K"
    return f"{value:,.0f}"


def quality_badge(value: str) -> str:
    return f"<span class='quality-badge'>{value}</span>"
