import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import plotly.graph_objects as go
from components.charts import create_time_series_chart
from components.maps import create_incidence_map

st.set_page_config(
    page_title="InfoDengue - Monitoramento Inteligente",
    page_icon="🦟",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data(ttl=3600)
def load_data():
    response = requests.get("http://localhost:8000/data")
    return pd.DataFrame(response.json())

def main():
    st.title("🦟 InfoDengue - Sistema de Monitoramento Inteligente")
    
    with st.sidebar:
        st.header("Filtros")
        estado = st.selectbox("Estado", ["Todos", "MG", "SP", "RJ"])
        periodo = st.slider("Período (dias)", 7, 365, 30)
    
    data = load_data()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Casos Hoje", "1,234", "12%")
    with col2:
        st.metric("Previsão 7 dias", "8,456", "23%")
    with col3:
        st.metric("Municípios em Alerta", "45", "-3")
    with col4:
        st.metric("Eficácia do Modelo", "89.2%", "1.2%")
    
    col1, col2 = st.columns(2)  # Fixed the typo here
    
    with col1:
        st.subheader("Tendência Temporal")
        chart = create_time_series_chart(data)
        st.plotly_chart(chart, use_container_width=True)
    
    with col2:
        st.subheader("Mapa de Incidência")
        map_fig = create_incidence_map(data)
        st.plotly_chart(map_fig, use_container_width=True)

if __name__ == "__main__":
    main()