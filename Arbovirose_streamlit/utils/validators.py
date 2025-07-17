# Arbovirose_streamlit/utils/validators.py
import re

def validate_api_response(response):
    """Valida a estrutura da resposta da API"""
    if not isinstance(response, dict):
        return False
    if "data" not in response:
        return False
    return True

def validate_db_connection_string(connection_string):
    """Valida formato da string de conexão"""
    pattern = r"^\w+://(\w+):(\w+)@[\w.-]+:\d+/\w+$"
    return re.match(pattern, connection_string) is not None
