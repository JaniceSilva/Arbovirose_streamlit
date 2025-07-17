import os

# Verifica se estamos no Render
IS_RENDER = os.getenv('RENDER', 'False').lower() == 'true'

# Configuração do banco de dados
if IS_RENDER:
    # Usará a variável de ambiente configurada em run_app.py
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/arbovirose.db")
else:
    # Configuração local
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'arbovirose.db')}"
