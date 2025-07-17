import sqlite3
import pandas as pd
from datetime import datetime
import logging
from pysus.online_data import Infodengue
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
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

def fetch_infodengue_data(disease="dengue", start_date="2023-01-01", end_date="2024-12-31"):
    """
    Fetch data from InfoDengue using PySUS.
    Returns a pandas DataFrame.
    """
    try:
        logger.info(f"Fetching {disease} data from {start_date} to {end_date}")
        # Example: Fetch data for specific states (MG, SP, RJ)
        states = ["MG", "SP", "RJ"]
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
        
        # Standardize column names to match epi_data table
        data = data.rename(columns={
            "SE": "data",  # Epidemiological week or date
            "casos": "casos_confirmados",
            "municipio_nome": "municipio",
            "uf": "estado"
        })
        # Convert date to ISO format
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

if __name__ == "__main__":
    populate_database()
Traceback (most recent call last):
  File "<string>", line 5, in <module>
ModuleNotFoundError: No module named 'pysus'
Integration with Project
