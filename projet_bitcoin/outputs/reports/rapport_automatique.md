# Rapport automatique - Analyse du Bitcoin par la méthode des centres mobiles

## Période analysée
- Début: 17/09/2014
- Fin: 26/12/2023
- Nombre d'observations: 3388

## Formules utilisées
- SMA: moyenne arithmétique des n valeurs précédentes.
- EMA: EMA_t = alpha * x_t + (1 - alpha) * EMA_(t-1).

## Indicateurs calculés
- Colonne SMA: `SMA_30`
- Colonne EMA: `EMA_30`
- Rendements journaliers, volatilité annualisée, drawdown et volume moyen.

## Résultats clés
- Prix final: 42,520.40 USD
- Rendement sur la période: 9,197.45%
- Volatilité annualisée: 70.69%
- Drawdown maximal: -83.40%

## Analyse automatique
- **Signal global (Tendance haussière)**: Le prix reste au-dessus des deux centres mobiles; l'EMA confirme une réaction rapide du marché.
- **Effet du lissage (Net)**: La SMA réduit la variabilité quotidienne d'environ 80.1%, contre 80.1% pour l'EMA.
- **Comparaison SMA vs EMA (EMA)**: La EMA est la plus proche du prix observé sur la période sélectionnée, donc elle réagit mieux aux mouvements récents.
- **Volatilité (Modérée)**: La volatilité récente est inférieure à sa médiane, ce qui donne un signal de marché plus stabilisé.

## Conclusion
Conclusion automatique: la méthode des centres mobiles indique une tendance haussière sur la période étudiée. La SMA fournit une lecture plus lissée de la tendance de fond, tandis que l'EMA réagit plus vite aux changements de prix. Cette complémentarité permet de distinguer le bruit quotidien du mouvement directionnel du Bitcoin.
