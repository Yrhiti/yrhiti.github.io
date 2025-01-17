Set-Content README.md @"
# Introduction
• Ce projet vise à développer une plateforme d'analyse des données agricoles en 
intégrant des données historiques et en temps réel. L'objectif est de faciliter la prise de 
décision pour les acteurs du secteur agricole.

## Objectifs principaux
1. Concevoir un tableau de bord interactif.
2. Analyser les tendances temporelles et spatiales.
3. Développer des outils de prédiction des risques agricoles.

## Méthodologie
### Environnement Technique
• Langage : Python 3.8 ou supérieur.
• Bibliothèques principales : Pandas, Numpy, Bokeh, Folium, Scikit-learn, Streamlit.
• Configuration minimale : 8 Go de RAM.

### Structure du Projet
• Dossiers principaux :
  - `data/` : Contient les fichiers CSV (cultures, météo, sols, rendements).
  - `src/` : Scripts Python pour la gestion des données, visualisations et génération 
    de rapports.
  - `notebooks/` : Analyses exploratoires.
  - `reports/` : Rapports générés.
"@
