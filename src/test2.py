import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from branca.colormap import LinearColormap

class AgriculturalAnalyzer:
    def __init__(self, data_manager):
        """
        Initialize the analyzer with the data manager.

        This class uses historical and current data to generate relevant agronomic insights.
        """
        self.data_manager = data_manager
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)

    def analyze_yield_factors(self, parcelle_id):
        """
        Analyze the factors influencing yields for a given parcel.
        """
        historical_data = self.data_manager.get_history()
        if parcelle_id not in historical_data:
            raise ValueError("Parcelle ID not found in historical data.")
        
        data = historical_data[parcelle_id]
        yield_data = data['yields']
        years = data['years']

        # Simulate environmental factors for demonstration
        weather_data = np.random.rand(len(years))
        soil_quality = np.random.rand(len(years))

        correlations = self._calculate_yield_correlations(yield_data, weather_data, soil_quality)
        limiting_factors = self._identify_limiting_factors(data, correlations)
        trends = self._analyze_performance_trend(data)

        return {
            "correlations": correlations,
            "limiting_factors": limiting_factors,
            "performance_trends": trends,
        }

    def _calculate_yield_correlations(self, yield_data, weather_data, soil_data):
        """
        Calculate correlations between yields and environmental factors.
        """
        weather_corr = pearsonr(yield_data, weather_data)[0]
        soil_corr = pearsonr(yield_data, soil_data)[0]
        return {"weather": weather_corr, "soil": soil_corr}

    def _identify_limiting_factors(self, parcelle_data, correlations):
        """
        Identify yield-limiting factors based on Liebig's Law of the Minimum.
        """
        limiting_factor = min(correlations, key=correlations.get)
        limiting_value = correlations[limiting_factor]
        return {limiting_factor: limiting_value}

    def _analyze_performance_trend(self, parcelle_data):
        """
        Analyze performance trends over time for the parcel.
        """
        years = parcelle_data['years']
        yields = parcelle_data['yields']
        trend = np.polyfit(years, yields, 1)[0]
        return {"trend_slope": trend, "trend_description": "Increasing" if trend > 0 else "Decreasing"}

    def create_streamlit_dashboard(self):
        """
        Create a Streamlit interface for analyzing yield factors.
        """
        st.title("Agricultural Analysis Dashboard")

        # Select a parcel
        parcels = list(self.data_manager.get_history().keys())
        selected_parcel = st.selectbox("Select a Parcel", options=parcels)

        # Display analysis results
        if st.button("Analyze"):
            try:
                analysis_results = self.analyze_yield_factors(selected_parcel)
                st.subheader(f"Analysis for Parcel: {selected_parcel}")

                # Display correlations
                st.write("### Correlations:")
                for factor, corr in analysis_results['correlations'].items():
                    st.write(f"- {factor.capitalize()}: {corr:.2f}")

                # Display limiting factors
                st.write("### Limiting Factors:")
                for factor, value in analysis_results['limiting_factors'].items():
                    st.write(f"- {factor.capitalize()}: {value:.2f}")

                # Display performance trends
                trends = analysis_results['performance_trends']
                st.write("### Performance Trends:")
                st.write(f"- Slope: {trends['trend_slope']:.2f}")
                st.write(f"- Description: {trends['trend_description']}")

            except ValueError as e:
                st.error(str(e))


# DataManager Class for Data Simulation
class DataManager:
    def __init__(self):
        self.data = {
            'history': {
                (46.2276, 2.2137): {'years': [2020, 2021, 2022], 'yields': [4, 6, 5], 'crops': ['wheat', 'barley', 'wheat']},
                (47.2138, 1.5375): {'years': [2020, 2021, 2022], 'yields': [7, 9, 8], 'crops': ['corn', 'soybean', 'corn']},
                (45.7640, 4.8357): {'years': [2020, 2021, 2022], 'yields': [11, 13, 12], 'crops': ['sunflower', 'wheat', 'sunflower']},
            }
        }

    def get_history(self):
        return self.data['history']


# Main Functionality
if __name__ == "__main__":
    data_manager = DataManager()
    analyzer = AgriculturalAnalyzer(data_manager)
    analyzer.create_streamlit_dashboard()