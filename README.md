# Analyse du Bitcoin par la méthode des centres mobiles

Projet universitaire complet en Data Science avec Streamlit, Pandas, NumPy et Plotly.

## Objectif

Analyser l'évolution du Bitcoin à partir du fichier `BTC-USD.csv` en appliquant la méthode des centres mobiles:

- SMA: Simple Moving Average
- EMA: Exponential Moving Average
- comparaison prix original, SMA et EMA
- exploration, statistiques descriptives, volatilité et volume
- génération automatique de graphiques, résultats CSV et rapport Markdown

## Structure

```text
projet_bitcoin/
├── app.py
├── BTC-USD.csv
├── requirements.txt
├── README.md
├── src/
│   ├── preprocessing.py
│   ├── indicators.py
│   ├── visualization.py
│   ├── analysis.py
│   └── utils.py
├── outputs/
│   ├── figures/
│   └── reports/
└── assets/
    └── style.css
```

## Installation

```bash
cd projet_bitcoin
pip install -r requirements.txt
```

## Lancement

```bash
streamlit run app.py
```

## Importation des données

Dans l'interface, la section **Source des données** se trouve en haut de la sidebar.

- Sans action de l'utilisateur, l'application charge automatiquement `BTC-USD.csv`.
- Pour une démonstration, il est aussi possible d'utiliser le bouton **Importer un fichier CSV**.
- Le CSV importé doit contenir au minimum les colonnes `Date`, `Open`, `High`, `Low`, `Close` et `Volume`.

## Fonctionnalités

- validation automatique du CSV
- import CSV optionnel depuis l'interface Streamlit
- nettoyage des dates, doublons, valeurs manquantes et colonnes numériques
- calcul des rendements, volatilité annualisée 30 jours, drawdown et volume moyen
- calcul dynamique de la SMA et de l'EMA
- graphiques interactifs Plotly en thème sombre
- zoom, hover interactif, range selector et candlestick OHLC
- dashboard premium avec sidebar, cartes KPI et analyse automatique
- sauvegarde automatique des figures en HTML dans `outputs/figures`
- export des résultats dans `outputs/reports/bitcoin_resultats_centres_mobiles.csv`
- rapport automatique dans `outputs/reports/rapport_automatique.md`

## Méthode

La SMA calcule la moyenne arithmétique des `n` valeurs précédentes:

```text
SMA_t = moyenne des n valeurs précédentes
```

L'EMA donne plus de poids aux observations récentes:

```text
EMA_t = alpha * x_t + (1 - alpha) * EMA_(t-1)
```

La comparaison SMA vs EMA permet de distinguer la tendance de fond et la réactivité aux mouvements récents du Bitcoin.
