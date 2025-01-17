import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
import warnings
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
import os

# Set the working directory to the data folder
os.chdir(r'C:/Users/RHITI/Yasser_viz/Yasser_viz/projet_agricole/data')

# Suppress warnings
warnings.filterwarnings('ignore')

class AgriculturalDataManager:
    def __init__(self):
        """Initializes the agricultural data manager."""
        self.monitoring_data = None
        self.weather_data = None
        self.soil_data = None
        self.yield_history = None
        self.scaler = StandardScaler()

    def load_data(self):
        """Loads all necessary data for the system."""
        try:
            self.monitoring_data = pd.read_csv('monitoring_cultures.csv', parse_dates=['date'])
            self.weather_data = pd.read_csv('meteo_detaillee.csv', parse_dates=['date'])
            self.soil_data = pd.read_csv('sols.csv')
            self.yield_history = pd.read_csv('historique_rendements.csv')

            # Ensure date column in yield_history is properly converted to datetime
            self.yield_history['date'] = pd.to_datetime(self.yield_history['date'], format='%Y-%m-%d')
            
            # Create the 'annee' column from the 'date' column
            self.yield_history['annee'] = self.yield_history['date'].dt.year
            
            # Extract month from 'date' to create 'month'
            self.yield_history['month'] = self.yield_history['date'].dt.month  # Extract month from date

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error loading data: {e}")

        # Check if 'annee' exists in yield_history
        if 'annee' not in self.yield_history.columns:
            raise KeyError("'annee' column is missing in yield_history.csv")

        self._setup_temporal_indices()
        self._verify_temporal_consistency()
        self._check_missing_values()
        self._check_unit_consistency()

    def _setup_temporal_indices(self):
        """Sets up temporal indices for different datasets."""
        self.monitoring_data.set_index('date', inplace=True)
        self.monitoring_data.sort_index(inplace=True)
        self.weather_data.set_index('date', inplace=True)
        self.weather_data.sort_index(inplace=True)

    def _verify_temporal_consistency(self):
        """Checks for temporal consistency between datasets."""
        monitoring_range = self.monitoring_data.index
        weather_range = self.weather_data.index
        if not (weather_range.min() <= monitoring_range.min() and weather_range.max() >= monitoring_range.max()):
            warnings.warn("Monitoring data extends beyond weather data range.")

    def _check_missing_values(self):
        """Checks for missing values in datasets."""
        for df_name, df in [("monitoring_data", self.monitoring_data),
                            ("weather_data", self.weather_data),
                            ("soil_data", self.soil_data),
                            ("yield_history", self.yield_history)]:
            missing = df.isnull().sum()
            if missing.any():
                print(f"Missing values in {df_name}:")
                print(missing[missing > 0])
            else:
                print(f"No missing values in {df_name}.")

    def _check_unit_consistency(self):
        """Checks for unit consistency in yield data."""
        yield_units = self.yield_history.groupby('annee')['rendement_estime'].mean()
        if yield_units.std() / yield_units.mean() > 0.5:
            warnings.warn("Potential inconsistency in yield units across years.")

    def prepare_features(self):
        """Prepares features by merging different datasets."""
        merged_data = pd.merge_asof(self.monitoring_data.reset_index(),
                                    self.weather_data.reset_index(),
                                    on='date',
                                    direction='nearest')
        merged_data = pd.merge(merged_data, self.soil_data, on='parcelle_id')
        return self._enrich_with_yield_history(merged_data)

    def _enrich_with_yield_history(self, data):
        """Enriches current data with historical yield information."""
        avg_yields = self.yield_history.groupby(['parcelle_id', 'culture'])['rendement_estime'].mean().reset_index()
        avg_yields.columns = ['parcelle_id', 'culture', 'historical_avg_yield']
        return pd.merge(data, avg_yields, on=['parcelle_id', 'culture'], how='left')

class AgriculturalDashboard:
    def __init__(self, data_manager):
        """Initializes the dashboard with the data manager."""
        self.data_manager = data_manager
        self.source = None
        self.hist_source = None
        self.create_data_sources()

    def create_data_sources(self):
        """Prepares Bokeh data sources."""        
        features = self.data_manager.prepare_features()
        self.source = ColumnDataSource(features)

        yield_history = self.data_manager.yield_history
        self.hist_source = ColumnDataSource(yield_history)

    def create_yield_history_plot(self):
        """Creates a plot showing historical yield evolution."""        
        p = figure(title='Yield History by Parcel',
                   x_axis_type='datetime',
                   height=400,
                   tools="pan,wheel_zoom,box_zoom,reset")

        p.line('annee', 'rendement_estime', source=self.hist_source, legend_label='Yield Estimate', line_width=2)
        p.circle('annee', 'rendement_estime', source=self.hist_source, size=8, color='red', legend_label='Yield Estimate')

        hover = HoverTool()
        hover.tooltips = [("Year", "@annee{%F}"), ("Yield Estimate", "@rendement_estime")]
        hover.formatters = {"@annee": "datetime"}
        p.add_tools(hover)

        return p

    def create_layout(self):
        """Organizes all plots into a coherent layout."""        
        yield_plot = self.create_yield_history_plot()
        layout = column(yield_plot)
        return layout

# Main execution
if __name__ == "__main__":
    # Initialize data manager
    data_manager = AgriculturalDataManager()
    data_manager.load_data()

    # Initialize dashboard
    dashboard = AgriculturalDashboard(data_manager)

    # Display the dashboard
    from bokeh.io import show
    show(dashboard.create_layout())