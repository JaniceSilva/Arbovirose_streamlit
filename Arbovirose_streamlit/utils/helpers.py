# Arbovirose_streamlit/utils/helpers.py
import requests
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

def get_api_data():
    """Obtém dados da API com tratamento de erros"""
    try:
        api_url = st.secrets["api"]["url"]
        api_key = st.secrets["api"]["key"]
        
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(api_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        return response.json()
    
    except KeyError:
        st.error("Chave API não configurada")
    except requests.exceptions.RequestException as e:
        st.error(f"Falha na API: {str(e)}")
    except ValueError:
        st.error("Resposta inválida da API")
    
    return None

def get_db_data():
    """Obtém dados do banco de dados com fallback"""
    try:
        engine = create_engine(st.secrets["database"]["url"])
        return pd.read_sql("SELECT * FROM epi_data", engine)
    
    except SQLAlchemyError as e:
        st.error(f"Erro no banco: {str(e)}")
        return None

def load_backup_data():
    """Carrega dados de backup locais"""
    try:
        return pd.read_csv("data/backup.csv")
    except FileNotFoundError:
        st.error("Dados de backup não encontrados")
        return pd.DataFrame()
