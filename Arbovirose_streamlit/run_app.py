import os
import subprocess
from multiprocessing import Process

def run_streamlit():
    os.chdir("Arbovirose_streamlit")
    subprocess.run([
        "streamlit", "run", "app.py",
        "--server.port", os.getenv("PORT", "8501")
    ])

def run_gunicorn():
    from app import health_app  # Importe seu app Flask
    health_app.run(host='0.0.0.0', port=8081)

if __name__ == "__main__":
    # Cria o banco se necessário
    os.makedirs("/var/lib/render/data", exist_ok=True)
    open("/var/lib/render/data/arbovirose.db", "a").close()
    os.chmod("/var/lib/render/data/arbovirose.db", 0o666)
    
    # Inicia os processos
    p1 = Process(target=run_streamlit)
    p2 = Process(target=run_gunicorn)
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
