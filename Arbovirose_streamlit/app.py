import streamlit as st
import pandas as pd
import sqlalchemy
import logging
from datetime import datetime
from components.charts import create_time_series_chart
from components.maps import create_incidence_map

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@st.cache_data(ttl=3600)
def get_realtime_data():
    """
    Fetch data from Render-hosted PostgreSQL database.
    Returns a pandas DataFrame or sample data if the query fails.
    """
    # Use Render's PostgreSQL connection string from .streamlit/secrets.toml
    # Format: postgresql://username:password@host:port/database
    # Get from Render Dashboard: Databases > Your Database > Connection Info
    # IMPORTANT: Replace the default connection string below with your actual Render credentials.
    connection_string = st.secrets.get("database", {}).get("connection_string", "postgresql://user:password@host:port/arboviroses")

    # Ensure psycopg2-binary is installed: pip install psycopg2-binary
    try:
        logger.info("Attempting to connect to Render PostgreSQL database...")
        engine = sqlalchemy.create_engine(connection_string)
        # Assuming your table name is 'epi_data'
        data = pd.read_sql('epi_data', engine)

        if 'data' in data.columns:
            data['data'] = pd.to_datetime(data['data'])
        else:
            logger.warning("Column 'data' not found in database. Please check your database schema.")

        # Save a backup of the fetched data
        data.to_json("backup_data.json", orient="records", date_format="iso")
        logger.info("Successfully fetched data from database and saved a backup.")
        return data
    except ImportError as e:
        st.error(f"Missing psycopg2 driver: {str(e)}. Please install it: `pip install psycopg2-binary`")
        logger.error(f"Import error: {str(e)}")
        return load_fallback_data()
    except (sqlalchemy.exc.OperationalError, sqlalchemy.exc.DatabaseError) as e:
        st.error(f"Database connection error: {str(e)}. Please check your Render connection string and database availability.")
        logger.error(f"Database error: {str(e)}")
        return load_fallback_data()
    except Exception as e:
        st.error(f"An unexpected error occurred while fetching data: {str(e)}")
        logger.error(f"Unexpected error: {str(e)}")
        return load_fallback_data()

def load_fallback_data():
    """
    Load cached data or sample data if database query fails.
    Returns a pandas DataFrame or None.
    """
    try:
        df = pd.read_json("backup_data.json", convert_dates=['data'])
        st.warning("⚠️ Using cached data due to a database connection issue.")
        logger.info("Successfully loaded cached data from 'backup_data.json'.")
        return df
    except (FileNotFoundError, ValueError) as e:
        st.warning("❗ No cached data available. Loading sample data for demonstration.")
        logger.warning(f"Cached data error: {str(e)}. Attempting to load sample data.")
        return load_sample_data()
    except Exception as e:
        st.error(f"Error loading fallback data: {str(e)}")
        logger.error(f"Fallback data loading error: {str(e)}")
        return None

def load_sample_data():
    """
    Load sample data for testing and demonstration purposes.
    Returns a pandas DataFrame.
    """
    try:
        sample_data = [
            {"estado": "MG", "municipio": "Belo Horizonte", "data": "2025-07-01", "casos_confirmados": 100},
            {"estado": "SP", "municipio": "São Paulo", "data": "2025-07-02", "casos_confirmados": 150},
            {"estado": "RJ", "municipio": "Rio de Janeiro", "data": "2025-07-03", "casos_confirmados": 80},
            {"estado": "MG", "municipio": "Uberlândia", "data": "2025-07-04", "casos_confirmados": 120},
            {"estado": "SP", "municipio": "Campinas", "data": "2025-07-05", "casos_confirmados": 90},
            {"estado": "RJ", "municipio": "Niterói", "data": "2025-07-06", "casos_confirmados": 70},
            {"estado": "MG", "municipio": "Belo Horizonte", "data": "2025-07-07", "casos_confirmados": 110},
        ]
        df = pd.DataFrame(sample_data)
        df['data'] = pd.to_datetime(df['data'])
        st.info("ℹ️ Using sample data for testing and demonstration.")
        logger.info("Successfully loaded sample data.")
        return df
    except Exception as e:
        st.error(f"Error loading sample data: {str(e)}")
        logger.error(f"Sample data loading error: {str(e)}")
        return None

def main():
    st.set_page_config(layout="wide", page_title="Dashboard de Monitoramento de Arboviroses")
    st.title("📊 Dashboard de Monitoramento de Arboviroses")
    st.markdown("""
    Este dashboard exibe dados de casos confirmados de arboviroses, com opções de filtro por estado,
    município e período. Os dados são obtidos em tempo real de um banco de dados PostgreSQL
    e podem usar dados em cache ou de exemplo em caso de falha na conexão.
    """)
    st.markdown("---")

    # Sidebar for filters
    with st.sidebar:
        st.header("Filtros de Dados")

        data = get_realtime_data() # Load data early to populate filters dynamically

        if data is None or data.empty:
            st.warning("Não foi possível carregar dados para os filtros. Exibindo filtros padrão.")
            all_estados = ["Todos", "MG", "SP", "RJ"]
            all_municipios = ["Todos", "Belo Horizonte", "São Paulo", "Rio de Janeiro", "Uberlândia", "Campinas", "Niterói"]
        else:
            all_estados = ["Todos"] + sorted(data['estado'].unique().tolist())
            # For municipalities, we'll populate them based on the selected state later
            all_municipios = ["Todos"]


        estado_selecionado = st.selectbox("Selecione o Estado:", all_estados)

        # Filter municipalities based on selected state
        municipios_disponiveis = ["Todos"]
        if estado_selecionado != "Todos" and data is not None and not data.empty:
            municipios_disponiveis.extend(sorted(data[data['estado'] == estado_selecionado]['municipio'].unique().tolist()))
        
        municipio_selecionado = st.selectbox("Selecione o Município:", municipios_disponiveis)

        periodo_dias = st.slider("Selecione o Período (dias):", min_value=7, max_value=365, value=30)
        st.markdown("---")
        st.info("Os dados são atualizados a cada hora (cache de 3600 segundos).")

    # --- Main Content Area ---
    if data is not None and not data.empty:
        # Apply filters to the data
        filtered_data = data.copy()

        if estado_selecionado != "Todos":
            filtered_data = filtered_data[filtered_data['estado'] == estado_selecionado]
        
        if municipio_selecionado != "Todos":
            filtered_data = filtered_data[filtered_data['municipio'] == municipio_selecionado]

        if 'data' in filtered_data.columns and not filtered_data['data'].empty:
            end_date = filtered_data['data'].max()
            start_date = end_date - pd.Timedelta(days=periodo_dias)
            filtered_data = filtered_data[(filtered_data['data'] >= start_date) & (filtered_data['data'] <= end_date)]
        else:
            st.warning("A coluna 'data' não está disponível ou está vazia nos dados filtrados, impedindo a filtragem por período.")
            logger.warning("Date column missing or empty in filtered data. Period filtering skipped.")

        if filtered_data.empty:
            st.warning("😔 Nenhum dado encontrado para os filtros selecionados. Tente ajustar os critérios de busca.")
            logger.info("No data found after applying filters.")
            return

        st.subheader("Visualizações de Dados")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Tendência de Casos Confirmados ao Longo do Tempo")
            try:
                # Assuming create_time_series_chart takes a DataFrame and returns a Plotly figure
                chart = create_time_series_chart(filtered_data)
                st.plotly_chart(chart, use_container_width=True)
            except Exception as e:
                st.error(f"❌ Erro ao gerar o gráfico de série temporal: {str(e)}")
                logger.error(f"Error generating time series chart: {str(e)}")

        with col2:
            st.markdown("#### Mapa de Incidência por Localização")
            try:
                # Assuming create_incidence_map takes a DataFrame and returns a Plotly figure (map)
                map_fig = create_incidence_map(filtered_data)
                st.plotly_chart(map_fig, use_container_width=True)
            except Exception as e:
                st.error(f"❌ Erro ao gerar o mapa de incidência: {str(e)}")
                logger.error(f"Error generating incidence map: {str(e)}")
        
        st.markdown("---")
        st.subheader("Dados Brutos (Amostra)")
        st.dataframe(filtered_data.head(10)) # Show only top 10 rows for brevity

    else:
        st.error("❌ Não foi possível carregar os dados para exibição do dashboard. Por favor, verifique a conexão com o banco de dados ou tente novamente mais tarde.")
        logger.critical("No data loaded at all. Dashboard cannot be displayed.")

if __name__ == "__main__":
    main()
