import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
import warnings
import os
warnings.filterwarnings('ignore')

# Définir le répertoire de travail
os.chdir(r'C:/Users/RHITI/Yasser_viz/Yasser_viz/projet_agricole/data')

class AgriculturalDataManager:
    def __init__(self):
        """Initialise le gestionnaire de données agricoles"""
        self.monitoring_data = None
        self.weather_data = None
        self.soil_data = None
        self.yield_history = None
        self.scaler = StandardScaler()

    def load_data(self):
        """ 
        Charge l'ensemble des données nécessaires au système
        Effectue les conversions de types et les indexations temporelles 
        """
        try:
            self.monitoring_data = pd.read_csv('monitoring_cultures.csv', parse_dates=['date'])
            self.weather_data = pd.read_csv('meteo_detaillee.csv', parse_dates=['date'])
            self.soil_data = pd.read_csv('sols.csv')
            self.yield_history = pd.read_csv('historique_rendements.csv')
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Erreur lors du chargement des données : {e}")

        self._setup_temporal_indices()
        self._verify_temporal_consistency()
        self._check_missing_values()
        self._check_unit_consistency()

    def _setup_temporal_indices(self):
        """Configure les index temporels pour les différentes séries de données et vérifie leur cohérence"""
        self.monitoring_data.set_index('date', inplace=True)
        self.monitoring_data.sort_index(inplace=True)
        self.weather_data.set_index('date', inplace=True)
        self.weather_data.sort_index(inplace=True)
        self.yield_history['mois'] = pd.to_datetime(self.yield_history['date']).dt.month

    def _verify_temporal_consistency(self):
        """Vérifie la cohérence des périodes temporelles entre les différents jeux de données"""
        monitoring_range = self.monitoring_data.index
        weather_range = self.weather_data.index
        if not (weather_range.min() <= monitoring_range.min() and weather_range.max() >= monitoring_range.max()):
            warnings.warn("Les données de monitoring dépassent la plage des données météo")

    def _check_missing_values(self):
        for df_name, df in [("monitoring_data", self.monitoring_data),
                            ("weather_data", self.weather_data),
                            ("soil_data", self.soil_data),
                            ("yield_history", self.yield_history)]:
            missing = df.isnull().sum()
            if missing.any():
                print(f"Valeurs manquantes dans {df_name}:")
                print(missing[missing > 0])
            else:
                print(f"Pas de valeurs manquantes dans {df_name}")

    def _check_unit_consistency(self):
        """Vérifie la cohérence des unités de rendement dans yield_history"""
        if 'rendement_final' not in self.yield_history.columns:
            print("La colonne 'rendement_final' est manquante dans 'yield_history'. Voici les colonnes disponibles :")
            print(self.yield_history.columns)
        else:
            yield_units = self.yield_history.groupby('mois')['rendement_final'].mean()
            if yield_units.std() / yield_units.mean() > 0.5:  # Seuil arbitraire de 50% de variation
                warnings.warn("Possible incohérence dans les unités de rendement entre les mois")

    def prepare_features(self):
        """Prépare les caractéristiques pour l'analyse en fusionnant les différentes sources de données"""
        merged_data = pd.merge_asof(self.monitoring_data.reset_index(),
                                    self.weather_data.reset_index(),
                                    on='date',
                                    direction='nearest')
        merged_data = pd.merge(merged_data, self.soil_data, on='parcelle_id')
        return self._enrich_with_yield_history(merged_data)

    def _enrich_with_yield_history(self, data):
        """Enrichit les données actuelles avec les informations historiques des rendements"""
        avg_yields = self.yield_history.groupby(['parcelle_id', 'culture'])['rendement_final'].mean().reset_index()
        avg_yields.columns = ['parcelle_id', 'culture', 'rendement_moyen_historique']
        return pd.merge(data, avg_yields, on=['parcelle_id', 'culture'], how='left')

    def get_temporal_patterns(self, parcelle_id):
        """Analyse les patterns temporels pour une parcelle donnée"""
        parcel_data = self.monitoring_data[self.monitoring_data['parcelle_id'] == parcelle_id]
        if len(parcel_data) < 2:
            raise ValueError("Données insuffisantes pour le calcul de tendance")

        rolling_metrics = parcel_data[['ndvi', 'lai', 'stress_hydrique', 'biomasse_estimee']].rolling(window=7).mean()
        time_index = (parcel_data.index - parcel_data.index[0]).days
        time_weights = np.exp(-(time_index.max() - time_index) / 365)  # Donne plus de poids aux données récentes
        trend = np.polyfit(time_index, parcel_data['biomasse_estimee'], 1, w=time_weights)
        slope = trend[0]
        variation = parcel_data['biomasse_estimee'].pct_change().mean()

        return rolling_metrics, {'pente': slope, 'variation_moyenne': variation}

    def calculate_risk_metrics(self, data, stress_weight=0.6, ndvi_weight=0.2, weather_weight=0.2):
        """Calcule les métriques de risque basées sur les conditions actuelles et l'historique"""
        data['ndvi_ecart'] = data['ndvi'] - data.groupby('parcelle_id')['ndvi'].transform('mean')
        data['extreme_weather'] = ((data['temperature'] > data['temperature'].quantile(0.95)) | 
                                   (data['precipitation'] > data['precipitation'].quantile(0.95))).astype(int)
        data['risk_score'] = (data['stress_hydrique'] * stress_weight + 
                              data['ndvi_ecart'].abs() * ndvi_weight +
                              data['extreme_weather'] * weather_weight) * 100
        return data

# Utilisation de la classe
data_manager = AgriculturalDataManager()
data_manager.load_data()

features = data_manager.prepare_features()

parcelle_id = 'P001'
history, trend = data_manager.get_temporal_patterns(parcelle_id)

risk_metrics = data_manager.calculate_risk_metrics(features)

print(f"Tendance de rendement : {trend['pente']:.2f} tonnes/ha/jour")
print(f"Variation moyenne : {trend['variation_moyenne']*100:.1f}%")

# Affichage des 5 premières lignes des métriques de risque
print("\nMétriques de risque (5 premières lignes) :")
print(risk_metrics[['parcelle_id', 'date', 'ndvi', 'stress_hydrique', 'extreme_weather', 'risk_score']].head())