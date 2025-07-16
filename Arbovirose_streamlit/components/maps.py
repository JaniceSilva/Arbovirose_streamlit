import folium
import streamlit_folium
import pandas as pd
import plotly.express as px

def create_incidence_map(data):
    """
    Create an incidence map for dengue cases by municipality.
    
    Args:
        data (pd.DataFrame): DataFrame with columns 'municipio', 'casos_confirmados', and optionally 'latitude', 'longitude'
    
    Returns:
        folium.Map or plotly.graph_objects.Figure: Folium map for geospatial data or Plotly scatter as fallback
    """
    # Check if geospatial data is available
    if 'latitude' in data.columns and 'longitude' in data.columns:
        # Create a Folium map centered on Brazil
        m = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)
        
        # Add markers for each municipality
        for _, row in data.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=row['casos_confirmados'] / 10,  # Scale radius by case count
                popup=f"{row['municipio']}: {row['casos_confirmados']} casos",
                color='red',
                fill=True,
                fill_color='red',
                fill_opacity=0.6
            ).add_to(m)
        
        return m
    else:
        # Fallback to Plotly scatter plot if no geospatial data
        fig = px.scatter(
            data,
            x='data',
            y='casos_confirmados',
            color='municipio',
            title="Incidência de Casos por Data (Fallback)",
            labels={'data': 'Data', 'casos_confirmados': 'Casos Confirmados'}
        )
        return fig