import os
import subprocess
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np


class AgriculturalReportGenerator:
    def __init__(self, analyzer, data_manager):
        """
        Initialise le générateur de rapports avec l'analyseur et le gestionnaire de données.
        """
        self.analyzer = analyzer
        self.data_manager = data_manager

    def generate_parcelle_report(self, parcelle_id):
        """
        Génère un rapport détaillé pour une parcelle donnée.

        Combine l'analyse historique, l'état actuel, et les recommandations futures.
        """
        st.title(f"Rapport détaillé pour la parcelle : {parcelle_id}")

        # Analyse de la parcelle
        try:
            analysis = self.analyzer.analyze_yield_factors(parcelle_id)
        except ValueError as e:
            st.error(str(e))
            return

        # État actuel
        current_state = self.data_manager.get_history().get(parcelle_id, {})

        # Génération du contenu Markdown
        markdown_content = self._create_markdown_report(parcelle_id, analysis, current_state)
        st.markdown(markdown_content, unsafe_allow_html=True)

        # Génération des visualisations
        self._generate_report_figures(parcelle_id, analysis)

        # Téléchargement du rapport PDF
        if st.button("Télécharger le rapport en PDF"):
            pdf_path = self._convert_to_pdf(markdown_content)
            if pdf_path:
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="Télécharger le rapport",
                        data=pdf_file,
                        file_name="rapport_agricole.pdf",
                        mime="application/pdf"
                    )

    def _create_markdown_report(self, parcelle_id, analysis, current_state):
        """
        Crée le contenu du rapport en format Markdown.
        """
        correlations = analysis.get("correlations", {})
        trends = analysis.get("performance_trends", {})
        limiting_factors = analysis.get("limiting_factors", {})

        markdown = f"""
        # Rapport pour la parcelle : {parcelle_id}

        ## Analyse Historique
        - **Corrélations :**
          - Climat : {correlations.get('weather', 'N/A'):.2f}
          - Sol : {correlations.get('soil', 'N/A'):.2f}
        - **Tendances :**
          - Pente : {trends.get('trend_slope', 'N/A'):.2f}
          - Description : {trends.get('trend_description', 'N/A')}

        ## Facteurs Limitants
        - Facteur limitant : {list(limiting_factors.keys())[0]} ({list(limiting_factors.values())[0]:.2f})

        ## Recommandations
        - Optimiser la qualité du sol en fonction des tendances historiques.
        - Mettre en place un système d'irrigation amélioré pendant les périodes sèches.

        **Date :** {datetime.now().strftime("%Y-%m-%d")}
        """
        return markdown

    def _generate_report_figures(self, parcelle_id, analysis):
        """
        Génère les visualisations pour le rapport.
        """
        # Évolution des rendements
        self._plot_yield_evolution(parcelle_id)

        # Matrice de corrélation
        correlations = analysis.get("correlations", {})
        self._plot_correlation_matrix(correlations)

    def _plot_yield_evolution(self, parcelle_id):
        """
        Crée un graphique détaillé de l'évolution des rendements.
        """
        history = self.data_manager.get_history().get(parcelle_id, {})
        years = history.get('years', [])
        yields = history.get('yields', [])

        plt.figure(figsize=(8, 5))
        sns.lineplot(x=years, y=yields, marker="o")
        plt.title("Évolution des rendements")
        plt.xlabel("Année")
        plt.ylabel("Rendement (tonnes/ha)")
        plt.grid()
        st.pyplot(plt)

    def _plot_correlation_matrix(self, correlation_data):
        """
        Crée une matrice de corrélation visuelle.
        """
        factors = list(correlation_data.keys())
        correlations = list(correlation_data.values())

        plt.figure(figsize=(5, len(factors)))
        sns.heatmap(
            [[c] for c in correlations],
            annot=True,
            fmt=".2f",
            yticklabels=factors,
            xticklabels=["Corrélation"]
        )
        plt.title("Matrice de corrélation")
        st.pyplot(plt)

    def _convert_to_pdf(self, markdown_content):
        """
        Convertit le rapport Markdown en PDF en utilisant Pandoc.
        """
        markdown_path = "rapport.md"
        pdf_path = "rapport_agricole.pdf"

        with open(markdown_path, "w") as md_file:
            md_file.write(markdown_content)

        try:
            subprocess.run(["pandoc", markdown_path, "-o", pdf_path], check=True)
            return pdf_path
        except subprocess.CalledProcessError:
            st.error("Erreur lors de la conversion du rapport en PDF. Assurez-vous que Pandoc est installé.")
            return None


# Exemple d'intégration dans Streamlit
class AgriculturalAnalyzer:
    def __init__(self, data_manager):
        self.data_manager = data_manager

    def analyze_yield_factors(self, parcelle_id):
        history = self.data_manager.get_history()
        if parcelle_id not in history:
            raise ValueError("Parcelle non trouvée.")
        return {
            "correlations": {"weather": 0.85, "soil": 0.65},
            "performance_trends": {"trend_slope": 0.5, "trend_description": "Increasing"},
            "limiting_factors": {"soil": 0.65}
        }


class DataManager:
    def __init__(self):
        self.data = {
            'history': {
                (46.2276, 2.2137): {'years': [2020, 2021, 2022], 'yields': [4, 6, 5]},
                (47.2138, 1.5375): {'years': [2020, 2021, 2022], 'yields': [7, 9, 8]},
                (45.7640, 4.8357): {'years': [2020, 2021, 2022], 'yields': [11, 13, 12]},
            }
        }

    def get_history(self):
        return self.data['history']


# Main Streamlit App
if __name__ == "__main__":
    data_manager = DataManager()
    analyzer = AgriculturalAnalyzer(data_manager)
    report_generator = AgriculturalReportGenerator(analyzer, data_manager)

    st.title("Générateur de rapports agricoles")

    # Sélection de la parcelle
    parcels = list(data_manager.get_history().keys())
    selected_parcel = st.selectbox("Sélectionnez une parcelle", options=parcels)

    # Génération du rapport
    if st.button("Générer le rapport"):
        report_generator.generate_parcelle_report(selected_parcel)