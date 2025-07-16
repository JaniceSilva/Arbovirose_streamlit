from datetime import datetime, timedelta
from data.collector import DataCollector
import pandas as pd
from config.settings import DATABASE_URL
from sqlalchemy import create_engine

class DailyUpdateJob:
    def __init__(self):
        self.collector = DataCollector()
        self.db_engine = create_engine(DATABASE_URL)
    
    def run_daily_update(self):
        print(f"Iniciando atualização diária - {datetime.now()}")
        try:
            new_data = self.collector.get_latest_data()
            self.clean_old_data()
            print("Atualização diária concluída com sucesso")
        except Exception as e:
            print(f"Erro na atualização diária: {e}")
    
    def clean_old_data(self):
        cutoff_date = datetime.now() - timedelta(days=5*365)
        for table in ['epi_data', 'climate_data']:
            query = f"DELETE FROM {table} WHERE data < '{cutoff_date}'"
            with self.db_engine.connect() as conn:
                conn.execute(query)
                conn.commit()

if __name__ == "__main__":
    job = DailyUpdateJob()
    job.run_daily_update()