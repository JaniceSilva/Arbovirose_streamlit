import sqlite3
import pandas as pd
import requests
import logging
from datetime import datetime, timedelta
import schedule
import time
import os

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_database():
    """
    Cria o banco arbovirose.db e a tabela epi_data se não existirem.
    """
    try:
        conn = sqlite3.connect("arbovirose.db")
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
        logger.info("Banco de dados e tabela epi_data criados ou verificados")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Erro ao criar banco de dados: {str(e)}")
        return None

def fetch_mosqlimate_data(disease="dengue", start_date=None, end_date=None):
    """
    Busca dados da API Mosqlimate.
    Retorna um pandas DataFrame.
    """
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        url = f"https://api.mosqlimate.org/data/{disease}?start_date={start_date}&end_date={end_date}"
        logger.info(f"Buscando dados do Mosqlimate: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = pd.DataFrame(response.json().get("items", []))
        if data.empty:
            logger.warning("API Mosqlimate retornou dados vazios")
            return None
        data = data.rename(columns={
            "uf": "estado",
            "municipio_nome": "municipio",
            "data": "data",
            "casos": "casos_confirmados"
        })
        if "data" in data.columns:
            data["data"] = pd.to_datetime(data["data"]).dt.strftime("%Y-%m-%d")
        logger.info(f"Obtidos {len(data)} registros do Mosqlimate")
        return data[["estado", "municipio", "data", "casos_confirmados"]]
    except Exception as e:
        logger.error(f"Erro ao buscar dados do Mosqlimate: {str(e)}")
        return None

def populate_database():
    """
    Popula arbovirose.db com dados do Mosqlimate.
    """
    conn = create_database()
    if not conn:
        logger.error("Falha ao criar ou conectar ao banco de dados")
        return
    
    data = fetch_mosqlimate_data()
    if data is None or data.empty:
        logger.warning("Nenhum dado para inserir no banco")
        conn.close()
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM epi_data")
        
        for _, row in data.iterrows():
            cursor.execute("""
                INSERT INTO epi_data (estado, municipio, data, casos_confirmados)
                VALUES (?, ?, ?, ?)
            """, (
                row["estado"],
                row["municipio"],
                row["data"],
                int(row.get("casos_confirmados", 0))
            ))
        conn.commit()
        logger.info(f"Inseridos {len(data)} registros na tabela epi_data")
    except sqlite3.Error as e:
        logger.error(f"Erro ao inserir dados: {str(e)}")
    finally:
        conn.close()

def keep_alive():
    """
    Ping na API para evitar parada no Render (free-tier).
    """
    try:
        response = requests.get("https://arbovirose-streamlit.onrender.com/ping")
        response.raise_for_status()
        logger.info("Ping keep-alive bem-sucedido")
    except Exception as e:
        logger.error(f"Falha no ping keep-alive: {str(e)}")

def job():
    """
    Trabalho diário para atualizar o banco e pingar a API.
    """
    logger.info("Iniciando atualização diária do banco")
    populate_database()
    keep_alive()
    logger.info("Atualização diária concluída")

def main():
    """
    Agenda o trabalho diário de atualização.
    """
    schedule.every().day.at("02:00").do(job)
    schedule.every(5).minutes.do(keep_alive)
    
    logger.info("Iniciando agendador")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    if os.getenv("MANUAL_RUN", "false").lower() == "true":
        job()
    else:
        main()
