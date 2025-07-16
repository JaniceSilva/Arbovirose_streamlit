import streamlit as st
import pandas as pd
import requests
from components.charts import create_time_series_chart
from components.maps import create_incidence_map

@st.cache_data(ttl=3600)
mport requests
import streamlit as st

def load_data():
    try:
        response = requests.get("YOUR_API_URL", timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except requests.exceptions.ConnectionError as e:
        st.error(f"Failed to connect to the API: {str(e)}. Please check your network or API availability.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"API returned an error: {str(e)}")
        return None
    except requests.exceptions.Timeout as e:
        st.error(f"Request timed out: {str(e)}. Please try again later.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"An unexpected error occurred while fetching data: {str(e)}")
        return None

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
