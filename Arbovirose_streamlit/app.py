import streamlit as st
import pandas as pd
import requests
import logging
import json
from datetime import datetime
from components.charts import create_time_series_chart
from components.maps import create_incidence_map

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@st.cache_data(ttl=3600)
def load_data(_url=None):  # REPLACE with actual API URL, e.g., from OPENDATASUS or SINAN
    """
    Fetch data from the API with robust error handling and caching.
    Returns a pandas DataFrame or sample data if the API URL is not provided or fails.
    """
    if _url is None:
        st.warning("No API URL provided. Using sample data for testing.")
        logger.info("No API URL provided. Loading sample data.")
        return load_sample_data()
    
    try:
        logger.info(f"Attempting to fetch data from API: {_url}")
        response = requests.get(_url, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()
        # Convert JSON to DataFrame (adjust based on actual JSON structure)
        df = pd.DataFrame(data)
        # Ensure 'data' column is in datetime format
        if 'data' in df.columns:
            df['data'] = pd.to_datetime(df['data'])
        # Cache the data locally as a fallback
        df.to_json("backup_data.json", orient="records", date_format="iso")
        return df
    except requests.exceptions.ConnectionError as e:
        st.error(f"Failed to connect to the API: {str(e)}. Please check your network or API availability.")
        logger.error(f"Connection error: {str(e)}")
        return load_fallback_data()
    except requests.exceptions.HTTPError as e:
        st.error(f"API returned an error: {str(e)}")
        logger.error(f"HTTP error: {str(e)}")
        return load_fallback_data()
    except requests.exceptions.Timeout as e:
        st.error(f"Request timed out: {str(e)}. Please try again later.")
        logger.error(f"Timeout error: {str(e)}")
        return load_fallback_data()
    except (requests.exceptions.RequestException, ValueError) as e:
        st.error(f"An unexpected error occurred while fetching or processing data: {str(e)}")
        logger.error(f"Unexpected error: {str(e)}")
        return load_fallback_data()

def load_fallback_data():
    """
    Load cached data or sample data as a fallback if the API request fails.
    Returns a pandas DataFrame or None if no data is available.
    """
    try:
        df = pd.read_json("backup_data.json", convert_dates=['data'])
        st.warning("Using cached data due to API failure.")
        logger.info("Loaded cached data from backup_data.json")
        return df
    except FileNotFoundError:
        st.warning("No cached data available. Loading sample data for testing.")
        logger.warning("No cached data found. Loading sample data.")
        return load_sample_data()
    except ValueError as e:
        st.error(f"Error reading cached data: {str(e)}")
        logger.error(f"Cached data error: {str(e)}")
        return load_sample_data()

def load_sample_data():
    """
    Load sample data for testing if no API or cached data is available.
    Returns a pandas DataFrame.
    """
    try:
        sample_data = [
            {"estado": "MG", "data": "2025-07-01", "casos": 100},
            {"estado": "SP", "data": "2025-07-02", "casos": 150},
            {"estado": "RJ", "data": "2025-07-03", "casos": 80},
            {"estado": "MG", "data": "2025-07-04", "casos": 120},
        ]
        df = pd.DataFrame(sample_data)
        df['data'] = pd.to_datetime(df['data'])
        st.info("Using sample data for testing purposes.")
        logger.info("Loaded sample data.")
        return df
    except Exception as e:
        st.error(f"Error loading sample data: {str(e)}")
        logger.error(f"Sample data error: {str(e)}")
        return None

def main():
    st.title("Dashboard de Arboviroses")
    
    # Sidebar for input controls
    with st.sidebar:
        st.header("Filtros")
        # State selection
        estados = ["Todos", "MG", "SP", "RJ"]
        estado = st.selectbox("Estado", estados)
        
        # Period slider (days)
        periodo = st.slider("Período (dias)", min_value=7, max_value=365, value=30)
    
    # Load data (set _url to the actual API endpoint, e.g., from OPENDATASUS or SINAN)
    data = load_data(_url=None)  # REPLACE None with actual API URL
    
    if data is not None and not data.empty:
        # Filter data by state
        if estado != "Todos":
            data = data[data['estado'] == estado]
        
        # Filter data by period
        if 'data' in data.columns:
            end_date = data['data'].max()
            start_date = end_date - pd.Timedelta(days=periodo)
            data = data[(data['data'] >= start_date) & (data['data'] <= end_date)]
        
        # Create and display charts
        try:
            chart = create_time_series_chart(data)
            map_fig = create_incidence_map(data)
            st.plotly_chart(chart, use_container_width=True)
            st.plotly_chart(map_fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating visualizations: {str(e)}")
            logger.error(f"Visualization error: {str(e)}")
    else:
        st.warning("Nenhum dado disponível para exibição.")

if __name__ == "__main__":
    main()
