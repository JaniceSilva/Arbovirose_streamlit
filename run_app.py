import os
import subprocess
from multiprocessing import Process
import time
import signal

def create_database():
    """Cria o banco de dados no diretório do projeto"""
    # Caminho dentro do espaço do projeto
    db_dir = os.path.join(os.getcwd(), "data")
    db_path = os.path.join(db_dir, "infodengue.db")
    
    os.makedirs(db_dir, exist_ok=True)
    
    if not os.path.exists(db_path):
        with open(db_path, "w") as f:
            pass  # Cria arquivo vazio
        os.chmod(db_path, 0o666)
        print(f"Banco criado em: {db_path}")
    else:
        print(f"Banco já existe em: {db_path}")
    
    # Configura a variável de ambiente
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    return db_path

def run_streamlit():
    """Executa o Streamlit"""
    print("Iniciando Streamlit...")
    subprocess.run([
        "streamlit", "run", "Arbovirose_streamlit/app.py",
        "--server.port", os.getenv("PORT", "8501")
    ])

def run_flask():
    """Executa o Flask para health checks"""
    print("Iniciando Flask...")
    from Arbovirose_streamlit.app import health_app
    
    # Configura para rodar na porta 5000
    health_app.run(host='0.0.0.0', port=5000)

def handler(signum, frame):
    """Manipula sinal de término"""
    print("Recebido sinal de término, encerrando...")
    exit(0)

if __name__ == "__main__":
    # Configura handler para sinais
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    
    # Cria o banco de dados
    db_path = create_database()
    print(f"Database configurado: {db_path}")
    
    # Inicia os processos
    p1 = Process(target=run_streamlit)
    p2 = Process(target=run_flask)
    
    p1.start()
    p2.start()
    
    try:
        # Mantém o processo principal ativo
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Encerrando...")
        p1.terminate()
        p2.terminate()
        exit(0)
