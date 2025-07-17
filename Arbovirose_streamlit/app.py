import streamlit as st
import pandas as pd
import requests
import logging
from datetime import datetime, timedelta
from components.charts import create_time_series_chart
from components.maps import create_incidence_map

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@st.cache_data(ttl=3600)
def get_realtime_data():
    """
    Busca dados da API hospedada no Render (arbovirose.db).
    Retorna um pandas DataFrame ou dados de exemplo se a consulta falhar.
    """
    api_url = st.secrets.get("api", {}).get("url", "https://arbovirose-streamlit.onrender.com/data_endpoint")
    try:
        logger.info(f"Buscando dados da API: {api_url}")
        response = requests.get(api_url)
        response.raise_for_status()
        data = pd.DataFrame(response.json())
        if 'data' in data.columns:
            data['data'] = pd.to_datetime(data['data'])
        data.to_json("backup_data.json", orient="records", date_format="iso")
        logger.info(f"Obtidos {len(data)} registros da API")
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Erro na API: {str(e)}. Verifique a disponibilidade da API ou URL.")
        logger.error(f"Erro na API: {str(e)}")
        return load_fallback_data()
    except Exception as e:
        st.error(f"Erro inesperado ao buscar dados: {str(e)}")
        logger.error(f"Erro inesperado: {str(e)}", exc_info=True)
        return load_fallback_data()

def load_fallback_data():
    """
    Carrega dados em cache ou dados de exemplo se a API falhar.
    Retorna um pandas DataFrame ou None.
    """
    try:
        df = pd.read_json("backup_data.json", convert_dates=['data'])
        st.warning("Usando dados em cache devido à falha na API.")
        logger.info("Dados em cache carregados")
        return df
    except (FileNotFileNotFoundError, ValueError) as e:
        st.warning("Nenhum dado em cache disponível. Usando dados de exemplo.")
        logger.warning(f"Erro nos dados em cache: {str(e)}. Carregando dados de exemplo.")
        return load_sample_data()

def load_sample_data():
    """
    Carrega dados de exemplo para teste.
    Retorna um pandas DataFrame.
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
        st.info("Usando dados de exemplo para teste.")
        logger.info("Dados de exemplo carregados")
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados de exemplo: {str(e)}")
        logger.error(f"Erro nos dados de exemplo: {str(e)}")
        return None

def test_api_connection(api_url=None):
    """
    Testa a conexão com a API do Render e verifica a atualidade dos dados.
    Exibe resultados no Streamlit e retorna True se bem-sucedido.
    """
    if api_url is None:
        api_url = st.secrets.get("api", {}).get("url", "https://arbovirose-streamlit.onrender.com/data_endpoint")
    try:
        logger.info(f"Testando conexão com a API: {api_url}")
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and "error" in data:
            st.error(f"API retornou erro: {data['error']}")
            logger.error(f"API retornou erro: {data['error']}")
            return False
        df = pd.DataFrame(data)
        if df.empty:
            st.error("API retornou dados vazios. Verifique se arbovirose.db está populado.")
            logger.warning("API retornou dados vazios")
            return False
        if 'data' in df.columns:
            df['data'] = pd.to_datetime(df['data'])
            latest_date = df['data'].max()
            current_date = datetime.now()
            if latest_date < current_date - timedelta(days=7):
                st.warning(f"Dados desatualizados. Última data: {latest_date}. Verifique o cron job daily_update.py.")
                logger.warning(f"Dados desatualizados. Última data: {latest_date}")
                return False
            else:
                st.success(f"Conexão com API bem-sucedida! Obtidos {len(df)} registros, última data: {latest_date}")
                logger.info(f"Conexão com API bem-sucedida. Obtidos {len(df)} registros, última data: {latest_date}")
                return True
        else:
            st.error("Resposta sem coluna 'data'")
            logger.error("Resposta sem coluna 'data'")
            return False
    except requests.exceptions.RequestException as e:
        st.error(f"Falha ao conectar à API: {str(e)}. Verifique o status da API no Render.")
        logger.error(f"Falha ao conectar à API: {str(e)}")
        return False
    except Exception as e:
        st.error(f"Erro inesperado: {str(e)}")
        logger.error(f"Erro inesperado: {str(e)}")
        return False

def main():
    """
    Função principal do aplicativo Streamlit.
    """
    st.title("📊 Dashboard de Monitoramento")

    # Sidebar para filtros e teste
    with st.sidebar:
        st.header("Filtros")
        estados = ["Todos", "MG", "SP", "RJ"]
        estado = st.selectbox("Estado", estados)
        periodo = st.slider("Período (dias)", min_value=7, max_value=365, value=30)
        if st.button("Testar Conexão com API"):
            test_api_connection()

    # Carregar dados
    data = get_realtime_data()

    if data is not None and not data.empty:
        # Aplicar filtros
        if estado != "Todos":
            data = data[data['estado'] == estado]
        if 'data' in data.columns:
            end_date = data['data'].max()
            start_date = end_date - pd.Timedelta(days=periodo)
            data = data[(data['data'] >= start_date) & (data['data'] <= end_date)]
        
        # Exibir visualizações
        try:
            chart = create_time_series_chart(data)
            map_fig = create_incidence_map(data)
            st.plotly_chart(chart, use_container_width=True)
            st.plotly_chart(map_fig, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao gerar visualizações: {str(e)}")
            logger.error(f"Erro de visualização: {str(e)}")
    else:
        st.warning("Nenhum dado disponível para exibição.")

if __name__ == "__main__":
    main()
