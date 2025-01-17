import folium
from folium import plugins
from branca.colormap import LinearColormap

class AgriculturalMap:
    def _init_(self, data_manager):
        """
        Initialize the map with the data manager.
        """
        self.data_manager = data_manager  # Expecting a pandas DataFrame with necessary data
        self.map = None
        self.yield_colormap = LinearColormap(
            colors=['red', 'yellow', 'green'],
            vmin=0,
            vmax=12,  # Maximum yield in tonnes/ha
            caption="Yield (tonnes/ha)"
        )

    def create_base_map(self, center_coords=[31.7917, -7.0926], zoom_start=6):
        """
        Create the base map centered on the provided coordinates.
        """
        self.map = folium.Map(location=center_coords, zoom_start=zoom_start, tiles="OpenStreetMap")

    def add_yield_history_layer(self):
        """
        Add a layer visualizing yield history.
        """
        for _, row in self.data_manager.iterrows():
            location = [row['latitude'], row['longitude']]
            yield_value = row.get('yield', 0)  # Replace 'yield' with your DataFrame's yield column name
            folium.CircleMarker(
                location=location,
                radius=8,
                color=self.yield_colormap(yield_value),
                fill=True,
                fill_opacity=0.7,
                popup=folium.Popup(f"Yield: {yield_value} tonnes/ha", max_width=200)
            ).add_to(self.map)

    def add_current_ndvi_layer(self):
        """
        Add a layer visualizing the current NDVI values.
        """
        for _, row in self.data_manager.iterrows():
            location = [row['latitude'], row['longitude']]
            ndvi_value = row.get('ndvi', 0)  # Replace 'ndvi' with your DataFrame's NDVI column name
            folium.CircleMarker(
                location=location,
                radius=8,
                color='blue',
                fill=True,
                fill_opacity=0.6,
                popup=folium.Popup(f"NDVI: {ndvi_value:.2f}", max_width=200)
            ).add_to(self.map)

    def add_risk_heatmap(self):
        """
        Add a heatmap layer to visualize risk areas.
        """
        heat_data = [[row['latitude'], row['longitude'], row.get('risk', 0)] for _, row in self.data_manager.iterrows()]
        plugins.HeatMap(heat_data, min_opacity=0.3, max_val=1.0, radius=15, blur=10).add_to(self.map)

    def get_map_html(self):
        """
        Return the HTML representation of the map.
        """
        return self.map.repr_html()

    def save_map(self, filepath="agricultural_map.html"):
        """
        Save the map to an HTML file.
        """
        self.map.save(filepath)


# Example Usage
if _name_ == "_main_":
    import pandas as pd

    # Example data
    data = {
        'latitude': [31.7917, 32.7940, 33.5731],
        'longitude': [-7.0926, -6.0240, -7.5898],
        'yield': [8, 10, 6],  # Example yield values
        'ndvi': [0.6, 0.8, 0.7],  # Example NDVI values
        'risk': [0.5, 0.3, 0.7]  # Example risk scores
    }
    df = pd.DataFrame(data)

    # Initialize and configure the map
    agricultural_map = AgriculturalMap(df)
    agricultural_map.create_base_map()
    agricultural_map.add_yield_history_layer()
    agricultural_map.add_current_ndvi_layer()
    agricultural_map.add_risk_heatmap()

    # Save or display the mapde
    agricultural_map.save_map()
    print("Map saved as 'agricultural_map.html'.")