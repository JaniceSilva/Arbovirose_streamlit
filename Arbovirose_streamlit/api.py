from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import pandas as pd
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://arboviroseapp.streamlit.app", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/data_endpoint")i
def get_epi_data():
    """
    Busca dados do arbovirose.db.
    Retorna dados JSON ou mensagem de erro.
    """
    try:
        conn = sqlite3.connect("arbovirose.db")
        data = pd.read_sql_query("SELECT * FROM epi_data", conn)
        conn.close()
        if data.empty:
            logger.warning("Nenhum dado encontrado na tabela epi_data")
            return {"error": "Nenhum dado encontrado na tabela epi_data"}
        logger.info(f"Servidos {len(data)} registros da tabela epi_data")
        return data.to_dict(orient="records")
    except Exception as e:
        logger.error(f"Erro ao buscar dados: {str(e)}")
        return {"error": str(e)}

@app.get("/ping")
def ping():
    """
    Endpoint de verificação de saúde.
    """
    return {"status": "ok"}
