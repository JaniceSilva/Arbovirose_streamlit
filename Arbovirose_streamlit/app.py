import streamlit as st
import pandas as pd
import requests
from components.charts import create_time_series_chart
from components.maps import create_incidence_map

@st.cache_data(ttl=3600)
def load_data():
    try:
        # Replace with your Render FastAPI URL
        response = requests.get("https://your-fastapi-app.onrender.com/data", timeout=10)
        response.raise_for_status()  # Raise exception for bad status codes
        data = pd.DataFrame(response.json())
        # Ensure 'data' column is datetime
        data['data'] = pd.to_datetime(data['data'])
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao carregar dados da API: {str(e)}")
        return pd.DataFrame()

def main():
    st.title("Dashboard de Arboviroses")
    
    # State selection
    estados = ["Todos", "MG", "SP", "RJ"]
    estado = st.selectbox("Estado", estados)
    
    # Period slider (days)
    periodo = st.slider("Período (dias)", min_value=7, max_value=365, value=30)
    
    # Load data
    data = load_data()
    
    if not data.empty:
        # Filter data by state
        if estado != "Todos":
            data = data[data['estado'] == estado]
        
        # Filter data by period
        end_date = data['data'].max()
        start_date = end_date - pd.Timedelta(days=periodo)
        data = data[(data['data'] >= start_date) & (data['data'] <= end_date)]
        
        # Create and display charts
        chart = create_time_series_chart(data)
        map_fig = create_incidence_map(data)
        st.plotly_chart(chart, use_container_width=True)
        st.plotly_chart(map_fig, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para exibição.")

if __name__ == "__main__":
    main()
