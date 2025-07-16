import os
from pathlib import Path

# Identifica se está no Render
IS_RENDER = os.getenv('RENDER', 'False').lower() == 'true'

# Configuração do banco de dados
if IS_RENDER:
    DATABASE_URL = os.getenv('DATABASE_URL')
else:
    # Desenvolvimento local
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATABASE_URL = f"sqlite:///{BASE_DIR}/arbovirose.db"
