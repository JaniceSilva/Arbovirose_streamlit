"""
Módulo com funções auxiliares reutilizáveis para a aplicação
"""

import pandas as pd
import streamlit as st
from datetime import datetime

def format_date(date_str: str) -> str:
    """
    Formata datas para o padrão brasileiro (DD/MM/YYYY)
    
    Args:
        date_str: Data em formato string
    
    Returns:
        Data formatada ou string original em caso de erro
    """
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return date_str

def display_dataframe(df: pd.DataFrame, max_rows: int = 10) -> None:
    """
    Exibe um DataFrame no Streamlit com formatação melhorada
    
    Args:
        df: DataFrame a ser exibido
        max_rows: Número máximo de linhas a mostrar
    """
    if df.empty:
        st.warning("Nenhum dado disponível para exibição.")
        return
    
    # Formata datas automaticamente
    date_cols = df.select_dtypes(include=['datetime']).columns
    for col in date_cols:
        df[col] = df[col].apply(format_date)
    
    st.dataframe(df.head(max_rows))

def calculate_growth(current: float, previous: float) -> float:
    """
    Calcula o crescimento percentual entre dois valores
    
    Args:
        current: Valor atual
        previous: Valor anterior
    
    Returns:
        Taxa de crescimento percentual (arredondada)
    """
    if previous == 0:
        return 0.0
    return round(((current - previous) / previous) * 100, 2)
