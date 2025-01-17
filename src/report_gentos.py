from bokeh.layouts import column, gridplot
from bokeh.models import (ColumnDataSource, Select, DateRangeSlider, 
                          HoverTool, ColorBar, LinearColorMapper, Range1d)
from bokeh.plotting import figure
from bokeh.palettes import RdYlBu11 as palette
import bokeh.plotting as bk
import pandas as pd
import numpy as np
from bokeh.io import show

class AgriculturalDashboard:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.source = None
        self.hist_source = None
        self.selected_parcelle = None
        self.create_data_sources()

    def create_data_sources(self):
        data = self.data_manager.prepare_features()
        self.source = ColumnDataSource(data)
        yield_data = self.data_manager.yield_history
        self.hist_source = ColumnDataSource(yield_data)

    def create_yield_history_plot(self):
        p = figure(title='Historique des Rendements par Parcelle',
                   x_range=Range1d(start=pd.to_datetime('2015-01-01'), end=pd.to_datetime('2022-12-31')), 
                   height=400, width=600)
        p.line('annee', 'rendement', source=self.hist_source, line_width=2, color='green')
        p.scatter('annee', 'rendement', source=self.hist_source, size=8, color='blue')
        p.add_tools(HoverTool(tooltips=[("Année", "@annee{%F}"), ("Rendement", "@rendement")],
                              formatters={'@annee': 'datetime'}, mode='vline'))
        return p

    def create_ndvi_temporal_plot(self):
        p = figure(title='Évolution du NDVI et Seuils Historiques',
                   x_range=Range1d(start=pd.to_datetime('2023-01-01'), end=pd.to_datetime('2023-12-31')), 
                   height=400, width=600)
        p.line('date', 'ndvi', source=self.source, line_width=2, color='blue', legend_label="NDVI")
        p.line('date', 'ndvi_ecart', source=self.source, line_dash='dashed', color='red', legend_label="Écart NDVI")
        p.add_tools(HoverTool(tooltips=[("Date", "@date{%F}"), ("NDVI", "@ndvi"), ("Écart NDVI", "@ndvi_ecart")],
                              formatters={'@date': 'datetime'}, mode='vline'))
        p.legend.location = "top_left"
        return p

    def create_stress_matrix(self):
        p = figure(title='Matrice de Stress', x_axis_label='Stress Hydrique',
                   y_axis_label='Conditions Météo', height=400, width=600)
        mapper = LinearColorMapper(palette=palette, low=0, high=100)
        p.scatter('stress_hydrique', 'extreme_weather', source=self.source, size=10,
                 color={'field': 'risk_score', 'transform': mapper}, fill_alpha=0.7)
        color_bar = ColorBar(color_mapper=mapper, label_standoff=12, location=(0, 0))
        p.add_layout(color_bar, 'right')
        return p

    def create_yield_prediction_plot(self):
        p = figure(title='Prédiction des Rendements',
                   x_range=Range1d(start=pd.to_datetime('2023-01-01'), end=pd.to_datetime('2023-12-31')), 
                   height=400, width=600)
        p.line('date', 'predicted_yield', source=self.source, line_width=2, color='purple', legend_label="Rendement Prédit")
        p.add_tools(HoverTool(tooltips=[("Date", "@date{%F}"), ("Rendement Prévu", "@predicted_yield")],
                              formatters={'@date': 'datetime'}, mode='vline'))
        p.legend.location = "top_left"
        return p

    def create_layout(self):
        yield_plot = self.create_yield_history_plot()
        ndvi_plot = self.create_ndvi_temporal_plot()
        stress_plot = self.create_stress_matrix()
        prediction_plot = self.create_yield_prediction_plot()
        layout = gridplot([[yield_plot, ndvi_plot], [stress_plot, prediction_plot]])
        return layout

    def get_parcelle_options(self):
        return sorted(self.data_manager.monitoring_data['parcelle_id'].unique())

    def prepare_stress_data(self):
        data = self.data_manager.calculate_risk_metrics(self.data_manager.prepare_features())
        self.source.data = data

    def update_plots(self, attr, old, new):
        self.selected_parcelle = new
        parcel_data = self.data_manager.monitoring_data[self.data_manager.monitoring_data['parcelle_id'] == new]
        self.source.data = parcel_data.to_dict('list')

class MockDataManager:
    def __init__(self):
        self.monitoring_data = pd.DataFrame({
            'parcelle_id': ['Parcelle 1'] * 10 + ['Parcelle 2'] * 10,
            'date': pd.date_range(start='2023-01-01', periods=10, freq='ME').tolist() * 2,
            'ndvi': np.random.rand(20),
            'ndvi_ecart': np.random.rand(20) - 0.5,
            'stress_hydrique': np.random.rand(20),
            'extreme_weather': np.random.rand(20),
            'risk_score': np.random.randint(0, 100, 20),
            'predicted_yield': np.random.rand(20) * 10,
        })
        
        # Corrected yield history data
        self.yield_history = pd.DataFrame({
            'annee': pd.date_range(start='2015-01-01', periods=8, freq='YE'),
            'rendement': np.random.rand(8) * 10,
        })
        
        # Ensure the month column is included
        self.yield_history['month'] = self.yield_history['annee'].dt.month

    def prepare_features(self):
        return self.monitoring_data

    def calculate_risk_metrics(self, data):
        return data

from bokeh.io import curdoc
from bokeh.models import Select
from bokeh.layouts import column

data_manager = MockDataManager()
dashboard = AgriculturalDashboard(data_manager)

parcelle_select = Select(title="Sélectionnez une parcelle",
                         value=dashboard.get_parcelle_options()[0],
                         options=dashboard.get_parcelle_options())

parcelle_select.on_change("value", dashboard.update_plots)

layout = column(parcelle_select, dashboard.create_layout())

# Use this to view the result
show(layout)