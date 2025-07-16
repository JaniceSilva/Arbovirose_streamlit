import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import create_engine
import streamlit as st
from config.settings import DATABASE_URL

class DataCollector:
    def __init__(self):
        self.db_engine = create_engine(DATABASE_URL)
    
    @st.cache_data(ttl=3600)
    def collect_epidemiological_data(self):
        """Simulate and collect epidemiological data."""
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        data = []
        for date in dates:
            casos = np.random.poisson(100) if date.month in [1, 2, 3, 4] else np.random.poisson(50)
            data.append({
                'data': date,
                'casos_confirmados': casos,
                'casos_suspeitos': casos * 1.5,
                'municipio': 'Ipatinga',
                'estado': 'MG'
            })
        df = pd.DataFrame(data)
        df.to_sql('epi_data', self.db_engine, if_exists='replace', index=False)
        return df
    
    @st.cache_data(ttl=1800)
    def collect_climate_data(self):
        """Simulate and collect climate data."""
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        data = []
        for date in dates:
            temp = 20 + 10 * np.sin(2 * np.pi * date.dayofyear / 365) + np.random.normal(0, 2)
            umidade = 60 + 20 * np.sin(2 * np.pi * date.dayofyear / 365) + np.random.normal(0, 5)
            chuva = max(0, np.random.exponential(2))
            data.append({
                'data': date,
                'temperatura': temp,
                'umidade': umidade,
                'precipitacao': chuva,
                'municipio': 'Ipatinga'
            })
        df = pd.DataFrame(data)
        df.to_sql('climate_data', self.db_engine, if_exists='replace', index=False)
        return df
    
    def get_latest_data(self):
        """Combine epidemiological and climate data from SQLite."""
        epi_data = pd.read_sql('epi_data', self.db_engine)
        climate_data = pd.read_sql('climate_data', self.db_engine)
        combined = epi_data.merge(climate_data, on=['data', 'municipio'], how='inner')
        return combined