# Rapport automatique - Analyse du Bitcoin par la méthode des centres mobiles

## Période analysée
- Début: 17/09/2014
- Fin: 16/02/2024
- Nombre d'observations: 3440

## Formules utilisées
- SMA: SMA_t = (x_t + x_(t-1) + ... + x_(t-n+1)) / n.
- EMA: EMA_t = alpha * x_t + (1 - alpha) * EMA_(t-1), avec alpha = 2 / (n + 1).

## Indicateurs calculés
- Colonne SMA: `SMA_30`
- Colonne EMA: `EMA_30`
- Rendements journaliers, volatilité annualisée, drawdown et volume moyen.

## Résultats clés
- Prix final: 51,841.06 USD
- Rendement sur la période: 11,235.49%
- Volatilité annualisée: 70.39%
- Drawdown maximal: -83.40%

## Analyse automatique
- **Signal global (Tendance haussière)**: Le prix reste au-dessus des deux centres mobiles; l'EMA confirme une réaction rapide du marché.
- **Effet du lissage (Net)**: La SMA réduit la variabilité quotidienne d'environ 80.1%, contre 80.1% pour l'EMA.
- **Comparaison SMA vs EMA (EMA)**: La EMA est la plus proche du prix observé sur la période sélectionnée, donc elle réagit mieux aux mouvements récents.
- **Volatilité (Modérée)**: La volatilité récente est inférieure à sa médiane, ce qui donne un signal de marché plus stabilisé.

## Conclusion
Conclusion automatique: la méthode des centres mobiles indique une tendance haussière sur la période étudiée. La SMA fournit une lecture plus lissée de la tendance de fond, tandis que l'EMA réagit plus vite aux changements de prix. Cette complémentarité permet de distinguer le bruit quotidien du mouvement directionnel du Bitcoin.
