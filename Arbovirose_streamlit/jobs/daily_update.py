import sqlite3
import pandas as pd
import logging
from datetime import datetime, timedelta
from pysus.online_data import Infodengue
import schedule
import time
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_database():
    """
    Create infodengue.db and epi_data table if they don't exist.
    """
    try:
        conn = sqlite3.connect("infodengue.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS epi_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estado TEXT,
                municipio TEXT,
                data TEXT,
                casos_confirmados INTEGER
            )
        """)
        conn.commit()
        logger.info("Database and epi_data table created or verified")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error creating database: {str(e)}")
        return None

def fetch_infodengue_data(disease="dengue", start_date=None, end_date=None):
    """
    Fetch data from InfoDengue using PySUS.
    Returns a pandas DataFrame.
    """
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        logger.info(f"Fetching {disease} data from {start_date} to {end_date}")
        states = ["MG", "SP", "RJ"]  # Adjust as needed
        dataframes = []
        for state in states:
            df = Infodengue.download(
                disease=disease,
                start_date=start_date,
                end_date=end_date,
                uf=state
            )
            dataframes.append(df)
        data = pd.concat(dataframes, ignore_index=True)
        
        # Standardize column names
        data = data.rename(columns={
            "SE": "data",
            "casos": "casos_confirmados",
            "municipio_nome": "municipio",
            "uf": "estado"
        })
        if "data" in data.columns:
            data["data"] = pd.to_datetime(data["data"]).dt.strftime("%Y-%m-%d")
        logger.info(f"Fetched {len(data)} rows from InfoDengue")
        return data[["estado", "municipio", "data", "casos_confirmados"]]
    except Exception as e:
        logger.error(f"Error fetching InfoDengue data: {str(e)}")
        return None

def populate_database():
    """
    Populate infodengue.db with data from InfoDengue.
    """
    conn = create_database()
    if not conn:
        return
    
    data = fetch_infodengue_data()
    if data is None or data.empty:
        logger.warning("No data to insert into database")
        conn.close()
        return
    
    try:
        cursor = conn.cursor()
        # Clear existing data (optional, comment out to append)
        cursor.execute("DELETE FROM epi_data")
        
        # Insert data
        for _, row in data.iterrows():
            cursor.execute("""
                INSERT INTO epi_data (estado, municipio, data, casos_confirmados)
                VALUES (?, ?, ?, ?)
            """, (
                row["estado"],
                row["municipio"],
                row["data"],
                row["casos_confirmados"]
            ))
        conn.commit()
        logger.info(f"Inserted {len(data)} rows into epi_data table")
    except sqlite3.Error as e:
        logger.error(f"Error inserting data: {str(e)}")
    finally:
        conn.close()

def job():
    """
    Daily job to update the database.
    """
    logger.info("Starting daily database update")
    populate_database()
    logger.info("Daily update completed")

def main():
    """
    Schedule the daily update job.
    """
    # Schedule job to run daily at 2:00 AM
    schedule.every().day.at("02:00").do(job)
    
    logger.info("Starting scheduler")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
