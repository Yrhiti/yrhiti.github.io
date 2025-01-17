import os
import pandas as pd
import streamlit as st
from bokeh.plotting import figure
from bokeh.embed import components
import folium

# Change to your data directory
os.chdir(r'C:/Users/RHITI/Yasser_viz/Yasser_viz/projet_agricole/data')

# Load the dataset
monit_cultures = pd.read_csv('monitoring_cultures.csv')

# Inspect the first few rows
st.write(monit_cultures.head())

class AgriculturalDashboard:
    def __init__(self):
        """Initialise les graphiques Bokeh."""
        self.plot = None

    def initialize_charts(self):
        """Créer un graphique Bokeh d'exemple."""
        self.plot = figure(title="Production Agricole", x_axis_label="Année", y_axis_label="Production (tonnes)")
        self.plot.line([2015, 2016, 2017, 2018, 2019, 2020], [100, 120, 130, 115, 140, 150], line_width=2)

    def update_charts(self, parcelle_id):
        """Met à jour les graphiques (exemple basique)."""
        if parcelle_id:
            self.plot.title.text = f"Production Agricole - Parcelle {parcelle_id}"


class AgriculturalMap:
    def __init__(self):
        """Initialise la carte Folium."""
        self.map = None

    def initialize_map(self):
        """Créer une carte Folium d'exemple."""
        # Set a default location for the map (can be adjusted based on your data)
        self.map = folium.Map(location=[31.7917, -7.0926], zoom_start=6)
        for _, row in monit_cultures.iterrows():
            # Adding markers from the CSV data for each parcel
            folium.Marker([row['latitude'], row['longitude']], popup=f"Parcelle {row['parcelle_id']}").add_to(self.map)

    def get_map_html(self):
        """Retourne l'HTML de la carte."""
        return self.map._repr_html_()

    def update_map(self, parcelle_id):
        """Met à jour la carte (exemple basique)."""
        if parcelle_id:
            # Find coordinates for the given parcelle_id
            parcelle_data = monit_cultures[monit_cultures['parcelle_id'] == parcelle_id].iloc[0]
            folium.Marker([parcelle_data['latitude'], parcelle_data['longitude']], popup=f"Parcelle {parcelle_id} mise à jour").add_to(self.map)


class IntegratedDashboard:
    def __init__(self):
        """Initialise le tableau de bord intégré."""
        self.bokeh_dashboard = AgriculturalDashboard()
        self.map_view = AgriculturalMap()

    def initialize_visualizations(self):
        """Initialise toutes les composantes visuelles."""
        self.bokeh_dashboard.initialize_charts()
        self.map_view.initialize_map()

    def create_streamlit_dashboard(self):
        """Crée une interface Streamlit intégrant toutes les visualisations."""
        st.title("Tableau de Bord Agricole Intégré")

        # Afficher le graphique Bokeh
        script, div = components(self.bokeh_dashboard.plot)
        st.markdown(script + div, unsafe_allow_html=True)

        # Afficher la carte Folium
        map_html = self.map_view.get_map_html()
        st.components.v1.html(map_html, height=600)

    def update_visualizations(self, parcelle_id):
        """Met à jour toutes les visualisations pour une parcelle donnée."""
        self.bokeh_dashboard.update_charts(parcelle_id)
        self.map_view.update_map(parcelle_id)

    def setup_interactions(self):
        """Configure les interactions."""
        parcelle_id = st.sidebar.text_input("ID de la parcelle", value="P001")
        if st.sidebar.button("Mettre à jour"):
            self.update_visualizations(parcelle_id)


# Création et affichage du tableau de bord
if __name__ == "__main__":
    dashboard = IntegratedDashboard()
    dashboard.initialize_visualizations()
    dashboard.setup_interactions()
    dashboard.create_streamlit_dashboard()