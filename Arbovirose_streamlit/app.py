import streamlit as st
import pandas as pd
import requests
import logging
from datetime import datetime
from components.charts import create_time_series_chart
from components.maps import create_incidence_map

import streamlit as st
from flask import Flask, Response

# Adicione isso no início do arquivo
import os
from flask import Flask, Response

# Configuração do health check
health_app = Flask(__name__)

@health_app.route('/healthz')
def health_check():
    return Response("OK", status=200)

# ... resto do seu código Streamlit ...

# app.py (Arbovirose_streamlit/app.py)
from flask import Flask, Response

# Crie o app Flask para health checks
health_app = Flask(__name__)

@health_app.route('/healthz')
def health_check():
    return Response("OK", status=200)

# Crie um servidor Flask oculto
flask_app = Flask(__name__)

@flask_app.route('/healthz')
def health_check():
    return Response("OK", status=200, mimetype='text/plain')

import sys
from flask import Flask, Response

# Adiciona o caminho de instalação do Gunicorn ao PATH
sys.path.append('/opt/render/.local/bin')

# Configuração do health check
health_app = Flask(__name__)

@health_app.route('/healthz')
def health_check():
    return Response("OK", status=200)

# ... resto do seu código Streamlit ...

# Inicie o Flask em uma thread separada
def run_flask_app():
    flask_app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    from threading import Thread
    Thread(target=run_flask_app).start()
    
    # Seu código Streamlit normal aqui
    st.title("Arbovirose Dashboard")
    # ... restante do seu código

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@st.cache_data(ttl=3600)
def get_realtime_data():
    """
    Fetch data from Render-hosted API serving arbovirose.db.
    Returns a pandas DataFrame or sample data if the query fails.
    """
    api_url = st.secrets.get("api", {}).get("url", "https://arbovirose-streamlit.onrender.com/data_endpoint")  # Replace with actual endpoint
    try:
        logger.info(f"Fetching data from API: {api_url}")
        response = requests.get(api_url)
        response.raise_for_status()  # Raise exception for 4xx/5xx errors
        data = pd.DataFrame(response.json())
        if 'data' in data.columns:
            data['data'] = pd.to_datetime(data['data'])
        data.to_json("backup_data.json", orient="records", date_format="iso")
        logger.info(f"Fetched {len(data)} rows from API")
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"API error: {str(e)}. Check Render API availability or URL.")
        logger.error(f"API error: {str(e)}")
        return load_fallback_data()
    except Exception as e:
        st.error(f"Unexpected error fetching data: {str(e)}")
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return load_fallback_data()

def load_fallback_data():
    """
    Load cached data or sample data if API query fails.
    Returns a pandas DataFrame or None.
    """
    try:
        df = pd.read_json("backup_data.json", convert_dates=['data'])
        st.warning("Using cached data due to API failure.")
        logger.info("Loaded cached data")
        return df
    except (FileNotFoundError, ValueError) as e:
        st.warning("No cached data available. Using sample data.")
        logger.warning(f"Cached data error: {str(e)}. Loading sample data.")
        return load_sample_data()

def load_sample_data():
    """
    Load sample data for testing.
    Returns a pandas DataFrame.
    """
    try:
        sample_data = [
            {"estado": "MG", "municipio": "Belo Horizonte", "data": "2025-07-01", "casos_confirmados": 100},
            {"estado": "SP", "municipio": "São Paulo", "data": "2025-07-02", "casos_confirmados": 150},
            {"estado": "RJ", "municipio": "Rio de Janeiro", "data": "2025-07-03", "casos_confirmados": 80},
            {"estado": "MG", "municipio": "Uberlândia", "data": "2025-07-04", "casos_confirmados": 120},
        ]
        df = pd.DataFrame(sample_data)
        df['data'] = pd.to_datetime(df['data'])
        st.info("Using sample data for testing.")
        logger.info("Loaded sample data")
        return df
    except Exception as e:
        st.error(f"Error loading sample data: {str(e)}")
        logger.error(f"Sample data error: {str(e)}")
        return None

def main():
    st.title("📊 Dashboard de Monitoramento")
    
    # Sidebar for filters
    with st.sidebar:
        st.header("Filtros")
        estados = ["Todos", "MG", "SP", "RJ"]
        estado = st.selectbox("Estado", estados)
        periodo = st.slider("Período (dias)", min_value=7, max_value=365, value=30)
        if st.button("Test API Connection"):
            try:
                response = requests.get(st.secrets["api"]["url"])
                response.raise_for_status()
                st.success("API connection successful!")
            except Exception as e:
                st.error(f"API connection failed: {str(e)}")
    
    # Load data
    data = get_realtime_data()
    
    if data is not None and not data.empty:
        # Apply filters
        if estado != "Todos":
            data = data[data['estado'] == estado]
        if 'data' in data.columns:
            end_date = data['data'].max()
            start_date = end_date - pd.Timedelta(days=periodo)
            data = data[(data['data'] >= start_date) & (data['data'] <= end_date)]
        
        # Display visualizations
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
