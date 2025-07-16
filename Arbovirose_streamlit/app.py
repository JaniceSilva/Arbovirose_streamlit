import streamlit as st
import pandas as pd
import requests
from components.charts import create_time_series_chart
from components.maps import create_incidence_map

@st.cache_data(ttl=3600)
def load_data():
    response = requests.get("https://seu-app-fastapi.onrender.com/data") # <-- ATUALIZE AQUI
    return pd.DataFrame(response.json())

def main():
    st.title("Dashboard de Arboviroses")
    estado = st.selectbox("Estado", ["Todos", "MG", "SP", "RJ"])
    periodo = st.slider("Período (dias)", 7, 365, 30)
    data = load_data()
    chart = create_time_series_chart(data)
    map_fig = create_incidence_map(data)
    st.plotly_chart(chart, use_container_width=True)
    st.plotly_chart(map_fig, use_container_width=True)

if __name__ == "__main__":
    main()
