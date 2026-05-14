from __future__ import annotations

from datetime import date
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

from src.analysis import analyze_trends, build_markdown_report, compute_kpis, descriptive_statistics
from src.indicators import add_moving_averages, moving_average_formula_text
from src.preprocessing import clean_bitcoin_data, load_csv
from src.utils import (
    ensure_directories,
    format_currency,
    format_number,
    format_percent,
    load_css,
    quality_badge,
    save_dataframe,
    save_plotly_figures,
    save_text_report,
)
from src.visualization import (
    create_candlestick_chart,
    create_ema_focus_chart,
    create_price_chart,
    create_sma_ema_comparison,
    create_sma_focus_chart,
    create_volatility_chart,
    create_volume_chart,
)


# Chemins centraux du projet. Ils évitent les chemins relatifs fragiles lorsque
# l'application est lancée depuis VS Code, un terminal ou Streamlit.
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "BTC-USD.csv"
ASSETS_DIR = BASE_DIR / "assets"
FIGURES_DIR = BASE_DIR / "outputs" / "figures"
REPORTS_DIR = BASE_DIR / "outputs" / "reports"


# Configuration globale de la page Streamlit. Aucun pictogramme n'est utilisé
# afin de conserver une interface sobre et adaptée à un rendu universitaire.
st.set_page_config(
    page_title="Analyse du Bitcoin - Centres mobiles",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner=False)
def get_clean_dataset(csv_path: str) -> tuple[pd.DataFrame, dict]:
    """Charge le fichier CSV local puis applique le pipeline de nettoyage."""
    raw_data = load_csv(csv_path)
    return clean_bitcoin_data(raw_data)


@st.cache_data(show_spinner=False)
def get_clean_uploaded_dataset(file_name: str, file_bytes: bytes) -> tuple[pd.DataFrame, dict]:
    """Nettoie un CSV importé depuis l'interface Streamlit."""
    raw_data = pd.read_csv(BytesIO(file_bytes))
    clean_data, quality_report = clean_bitcoin_data(raw_data)
    quality_report["source_name"] = file_name
    return clean_data, quality_report


@st.cache_data(show_spinner=False)
def get_indicator_dataset(df: pd.DataFrame, sma_window: int, ema_span: int) -> tuple[pd.DataFrame, str, str]:
    """Calcule les centres mobiles avec mise en cache pour fluidifier l'interface."""
    return add_moving_averages(df, sma_window=sma_window, ema_span=ema_span)


def inject_css() -> None:
    """Injecte la feuille de style premium dans l'application Streamlit."""
    css_content = load_css(ASSETS_DIR / "style.css")
    if css_content:
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


def render_hero() -> None:
    """Affiche l'en-tête principal du dashboard."""
    st.markdown(
        """
        <div class="hero-panel">
          <div class="hero-content">
            <div class="eyebrow">Dashboard Data Science - Finance quantitative - Bitcoin</div>
            <h1 class="hero-title">Analyse du Bitcoin par la méthode des centres mobiles</h1>
            <p class="hero-subtitle">
              Application analytique Streamlit dédiée au lissage des séries temporelles:
              exploration, statistiques descriptives, volatilité, SMA, EMA, comparaison
              interactive et génération automatique de conclusions.
            </p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, delta: str | None = None) -> None:
    """Rend une carte KPI homogène pour les indicateurs financiers clés."""
    delta_html = f"<div class='metric-delta'>{delta}</div>" if delta else ""
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-label">{label}</div>
          <div class="metric-value">{value}</div>
          {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_analysis_card(title: str, status: str, description: str) -> None:
    """Rend une carte d'interprétation automatique de la tendance."""
    st.markdown(
        f"""
        <div class="analysis-card">
          <div class="analysis-title">{title}</div>
          <div class="analysis-status">{status}</div>
          <div class="analysis-text">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def normalize_date_selection(selection: object, min_date: date, max_date: date) -> tuple[date, date]:
    """Sécurise la sélection de période lorsque Streamlit renvoie une valeur incomplète."""
    if isinstance(selection, tuple) and len(selection) == 2:
        start_date, end_date = selection
        return start_date or min_date, end_date or max_date
    return min_date, max_date


def filter_by_dates(df: pd.DataFrame, start_date: date, end_date: date) -> pd.DataFrame:
    """Filtre les données selon la période choisie dans la sidebar."""
    date_series = df["Date"].dt.date
    return df[(date_series >= start_date) & (date_series <= end_date)].copy()


def main() -> None:
    """Point d'entrée du dashboard analytique."""
    inject_css()
    ensure_directories(FIGURES_DIR, REPORTS_DIR)

    # La sidebar centralise les entrées utilisateur: source du CSV, fenêtres
    # SMA/EMA, période d'analyse et options d'affichage.
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
              <h2>Bitcoin Analytics Lab</h2>
              <p>Méthode des centres mobiles - SMA - EMA - Volatilité</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.subheader("Source des données")
        st.caption("Par défaut, l'application charge automatiquement le fichier local BTC-USD.csv.")
        uploaded_file = st.file_uploader(
            "Importer un fichier CSV",
            type=["csv"],
            help="Laissez vide pour utiliser directement le fichier BTC-USD.csv du projet.",
        )

        # Le CSV local reste la source par défaut, conformément au cahier des
        # charges. L'import manuel sert uniquement à tester un fichier compatible.
        if uploaded_file is None:
            source_name = "BTC-USD.csv"
            st.markdown(quality_badge("Chargement automatique"), unsafe_allow_html=True)
        else:
            source_name = uploaded_file.name
            st.markdown(quality_badge("Import depuis l'interface"), unsafe_allow_html=True)

    # Le pipeline accepte deux sources: le CSV local versionné dans le projet ou
    # un fichier importé par l'utilisateur avec les mêmes colonnes financières.
    with st.spinner(f"Chargement et nettoyage du fichier {source_name}..."):
        try:
            if uploaded_file is None:
                clean_df, quality_report = get_clean_dataset(str(DATA_PATH))
                quality_report["source_name"] = "BTC-USD.csv"
            else:
                clean_df, quality_report = get_clean_uploaded_dataset(uploaded_file.name, uploaded_file.getvalue())
        except Exception as exc:
            st.error(f"Impossible de charger le fichier {source_name}: {exc}")
            st.stop()

    min_date = clean_df["Date"].min().date()
    max_date = clean_df["Date"].max().date()

    # Les paramètres SMA et EMA sont dynamiques. Chaque changement déclenche un
    # recalcul des centres mobiles, des graphiques et de l'analyse automatique.
    with st.sidebar:
        st.divider()
        st.subheader("Paramètres")
        sma_window = st.slider("Fenêtre SMA", min_value=7, max_value=200, value=30, step=1)
        ema_span = st.slider("Période EMA", min_value=7, max_value=200, value=30, step=1)
        date_selection = st.date_input(
            "Période d'analyse",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
        auto_save = st.toggle("Sauvegarder automatiquement les exports", value=True)
        show_data = st.toggle("Afficher la table des données", value=False)

        st.divider()
        st.markdown("**Qualité du CSV**")
        st.markdown(quality_badge("CSV validé"), unsafe_allow_html=True)
        st.caption(f"Source active: {quality_report.get('source_name', source_name)}")
        st.caption(f"Lignes après nettoyage: {quality_report['rows_after']:,}")
        st.caption(f"Doublons supprimés: {quality_report['duplicate_dates_removed']}")
        st.caption(f"Dates invalides supprimées: {quality_report['invalid_dates_removed']}")

    # Les centres mobiles sont calculés sur les données nettoyées avant le filtre
    # de dates afin de conserver un historique suffisant au début de la période.
    with st.spinner("Calcul des centres mobiles SMA et EMA..."):
        indicator_df, sma_column, ema_column = get_indicator_dataset(clean_df, sma_window, ema_span)

    start_date, end_date = normalize_date_selection(date_selection, min_date, max_date)
    filtered_df = filter_by_dates(indicator_df, start_date, end_date)

    if filtered_df.empty:
        st.warning("Aucune donnée disponible sur la période sélectionnée.")
        st.stop()

    # Les KPI, interprétations textuelles et rapports sont recalculés sur la
    # période filtrée pour rester cohérents avec les graphiques affichés.
    kpis = compute_kpis(filtered_df)
    trend_analysis = analyze_trends(filtered_df, sma_column, ema_column)
    report_markdown = build_markdown_report(filtered_df, kpis, trend_analysis, sma_column, ema_column)

    # Les figures Plotly sont conservées dans un dictionnaire pour faciliter
    # l'affichage par onglets et la sauvegarde automatique en HTML.
    figures = {
        "01_courbe_prix_bitcoin_sma_ema": create_price_chart(filtered_df, sma_column, ema_column),
        "02_sma_30_jours": create_sma_focus_chart(filtered_df, sma_column),
        "03_ema_30_jours": create_ema_focus_chart(filtered_df, ema_column),
        "04_comparaison_sma_ema": create_sma_ema_comparison(filtered_df, sma_column, ema_column),
        "05_volume_transactions": create_volume_chart(filtered_df),
        "06_volatilite": create_volatility_chart(filtered_df),
        "07_ohlc_centres_mobiles": create_candlestick_chart(filtered_df, sma_column, ema_column),
    }

    result_csv_path = REPORTS_DIR / "bitcoin_resultats_centres_mobiles.csv"
    report_path = REPORTS_DIR / "rapport_automatique.md"

    if auto_save:
        try:
            save_plotly_figures(figures, FIGURES_DIR)
            save_dataframe(indicator_df, result_csv_path)
            save_text_report(report_markdown, report_path)
        except Exception as exc:
            st.toast(f"Export automatique non finalisé: {exc}")

    render_hero()

    metric_columns = st.columns(4)
    with metric_columns[0]:
        render_metric_card("Prix final", format_currency(kpis.get("latest_close")), format_percent(kpis.get("period_return")))
    with metric_columns[1]:
        render_metric_card("Volatilité annualisée", format_percent(kpis.get("annualized_volatility")), "Rolling 30 jours")
    with metric_columns[2]:
        render_metric_card("Drawdown maximal", format_percent(kpis.get("max_drawdown")), "Risque baissier")
    with metric_columns[3]:
        render_metric_card("Volume moyen", format_number(kpis.get("average_volume")), f"{kpis.get('observations', 0):,} observations")

    st.write("")
    formulas = moving_average_formula_text()
    formula_columns = st.columns(2)
    with formula_columns[0]:
        # SMA: moyenne simple des n dernières clôtures. Elle lisse fortement le
        # bruit quotidien et représente la tendance moyenne sur la fenêtre.
        st.markdown(f"<div class='formula-box'>{formulas['SMA']}</div>", unsafe_allow_html=True)
    with formula_columns[1]:
        # EMA: moyenne récursive pondérée. Le coefficient alpha donne davantage
        # d'importance aux observations récentes que la SMA.
        st.markdown(f"<div class='formula-box'>{formulas['EMA']}</div>", unsafe_allow_html=True)

    overview_tab, centers_tab, risk_tab, report_tab = st.tabs(
        ["Vue générale", "Centres mobiles", "Volatilité & volume", "Rapport & données"]
    )

    plot_config = {"displayModeBar": True, "scrollZoom": True, "responsive": True}

    with overview_tab:
        st.plotly_chart(figures["01_courbe_prix_bitcoin_sma_ema"], use_container_width=True, config=plot_config)
        insight_columns = st.columns(4)
        for column, insight in zip(insight_columns, trend_analysis.get("insights", [])):
            with column:
                render_analysis_card(insight.title, insight.status, insight.description)

    with centers_tab:
        left, right = st.columns(2)
        with left:
            st.plotly_chart(figures["02_sma_30_jours"], use_container_width=True, config=plot_config)
        with right:
            st.plotly_chart(figures["03_ema_30_jours"], use_container_width=True, config=plot_config)
        st.plotly_chart(figures["04_comparaison_sma_ema"], use_container_width=True, config=plot_config)

    with risk_tab:
        st.plotly_chart(figures["07_ohlc_centres_mobiles"], use_container_width=True, config=plot_config)
        left, right = st.columns(2)
        with left:
            st.plotly_chart(figures["05_volume_transactions"], use_container_width=True, config=plot_config)
        with right:
            st.plotly_chart(figures["06_volatilite"], use_container_width=True, config=plot_config)

    with report_tab:
        st.subheader("Résumé automatique")
        st.info(trend_analysis.get("conclusion", "Conclusion non disponible."))

        stats = descriptive_statistics(filtered_df)
        st.subheader("Statistiques descriptives")
        st.dataframe(stats, use_container_width=True, hide_index=True)

        csv_data = indicator_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Exporter les résultats CSV",
            data=csv_data,
            file_name="bitcoin_resultats_centres_mobiles.csv",
            mime="text/csv",
            type="primary",
        )
        st.download_button(
            "Exporter le rapport Markdown",
            data=report_markdown.encode("utf-8"),
            file_name="rapport_automatique_bitcoin.md",
            mime="text/markdown",
        )

        if show_data:
            st.subheader("Données préparées")
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)

        st.caption(f"Figures sauvegardées dans: {FIGURES_DIR}")
        st.caption(f"Rapports sauvegardés dans: {REPORTS_DIR}")


if __name__ == "__main__":
    main()
