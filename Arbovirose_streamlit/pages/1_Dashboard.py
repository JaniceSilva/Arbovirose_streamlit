import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
from config.settings import DATABASE_URL
from sqlalchemy import create_engine

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Dashboard de Monitoramento")

@st.cache_data(ttl=60)
def get_realtime_data():
    engine = create_engine(DATABASE_URL)
    @st.cache_data(ttl=60)
def get_realtime_data():
    try:
        engine = create_engine(DATABASE_URL)
        data = pd.read_sql('SELECT * FROM epi_data', engine)
        return data.assign(previsao=lambda x: x['casos_confirmados'] * (1 + ...))
    
    except SQLAlchemyError as e:
        st.error(f"Erro no banco de dados: {str(e)}")
        # Carregar dados de backup ou amostra
        return load_backup_data()

if st.button("🔄 Atualizar Dados"):
    st.cache_data.clear()
    st.rerun()

data = get_realtime_data()

col1, col2, col3, col4 = st.columns(4)

with col1:
    casos_hoje = data['casos_confirmados'].iloc[-1]
    casos_ontem = data['casos_confirmados'].iloc[-2]
    delta_casos = casos_hoje - casos_ontem
    st.metric("Casos Hoje", f"{casos_hoje:,}", f"{delta_casos:+.0f}")

with col2:
    previsao_7d = data['previsao'].tail(7).sum()
    st.metric("Previsão 7 dias", f"{previsao_7d:,.0f}", "23%")

with col3:
    municipios_alerta = 45
    st.metric("Municípios em Alerta", municipios_alerta, "-3")

with col4:
    eficacia = 89.2
    st.metric("Eficácia do Modelo", f"{eficacia:.1f}%", "1.2%")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Tendência vs Previsão")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['data'],
        y=data['casos_confirmados'],
        mode='lines+markers',
        name='Casos Reais',
        line=dict(color='blue')
    ))
    fig.add_trace(go.Scatter(
        x=data['data'],
        y=data['previsao'],
        mode='lines+markers',
        name='Previsão',
        line=dict(color='red', dash='dash')
    ))
    fig.update_layout(
        title="Casos Confirmados vs Previsão",
        xaxis_title="Data",
        yaxis_title="Número de Casos",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Distribuição por Região")
    regioes = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul']
    casos_regiao = [np.random.randint(100, 1000) for _ in regioes]
    fig = px.pie(values=casos_regiao, names=regioes, title="Distribuição de Casos por Região")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("🚨 Alertas Ativos")
alertas = pd.DataFrame({
    'Município': ['Ipatinga', 'Coronel Fabriciano', 'Timóteo', 'Santana do Paraíso'],
    'Estado': ['MG', 'MG', 'MG', 'MG'],
    'Nível': ['Alto', 'Médio', 'Alto', 'Baixo'],
    'Casos': [156, 89, 134, 34],
    'Tendência': ['↗️', '↘️', '↗️', '→']
})
st.dataframe(alertas, use_container_width=True, hide_index=True)

if st.checkbox("Auto-refresh (30s)"):
    import time
    time.sleep(30)
    st.rerun()
