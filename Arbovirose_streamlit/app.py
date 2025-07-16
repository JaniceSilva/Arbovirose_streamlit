import streamlit as st
import pandas as pd
import sqlalchemy
import logging
from datetime import datetime
from components.charts import create_time_series_chart
from components.maps import create_incidence_map

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@st.cache_data(ttl=3600)
def get_realtime_data():
    """
    Fetch data from the database with robust error handling and caching.
    Returns a pandas DataFrame or sample data if the query fails.
    """
    # Replace with your actual database connection string
    # Example for PostgreSQL: "postgresql://user:password@host:port/database"
    # Example for MySQL: "mysql+pymysql://user:password@host:port/database"
    connection_string = "postgresql://user:password@localhost:5432/arboviroses"  # UPDATE THIS
    try:
        logger.info("Attempting to connect to database and fetch epi_data")
        engine = sqlalchemy.create_engine(connection_string)
        data = pd.read_sql('epi_data', engine)
        # Ensure ' ..

data' column is in datetime format
        if 'data' in data.columns:
            data['data'] = pd.to_datetime(data['data'])
        # Cache the data locally as a fallback
        data.to_json("backup_data.json", orient="records", date_format="iso")
        logger.info("Successfully fetched data from database")
        return data
    except sqlalchemy.exc.OperationalError as e:
        st.error(f"Failed to connect to the database: {str(e)}. Please check your database configuration or network.")
        logger.error(f"Database connection error: {str(e)}")
        return load_fallback_data()
    except sqlalchemy.exc.DatabaseError as e:
        st.error(f"Database error: {str(e)}")
        logger.error(f"Database error: {str(e)}")
        return load_fallback_data()
    except Exception as e:
        st.error(f"An unexpected error occurred while fetching data: {str(e)}")
        logger.error(f"Unexpected error: {str(e)}")
        return load_fallback_data()

def load_fallback_data():
    """
    Load cached data or sample data as a fallback if the database query fails.
    Returns a pandas DataFrame or None if no data is available.
    """
    try:
        df = pd.read_json("backup_data.json", convert_dates=['data'])
        st.warning("Using cached data due to database failure.")
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
    Load sample data for testing if no database or cached data is available.
    Returns a pandas DataFrame.
    """
    try:
        sample_data = [
            {"estado": "MG", "data": "2025-07-01", "casos_confirmados": 100},
            {"estado": "SP", "data": "2025-07-02", "casos_confirmados": 150},
            {"estado": "RJ", "data": "2025-07-03", "casos_confirmados": 80},
            {"estado": "MG", "data": "2025-07-04", "casos_confirmados": 120},
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
    st.title("📊 Dashboard de Monitoramento")
    
    # Sidebar for input controls
    with st.sidebar:
        st.header("Filtros")
        # State selection
        estados = ["Todos", "MG", "SP", "RJ"]
        estado = st.selectbox("Estado", estados)
        
        # Period slider (days)
        periodo = st.slider("Período (dias)", min_value=7, max_value=365, value=30)
    
    # Load data
    data = get_realtime_data()
    
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
