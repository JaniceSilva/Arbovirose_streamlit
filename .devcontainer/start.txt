#!/bin/bash

# Instala dependências (garantia extra)
pip install -r Arbovirose_streamlit/requirements.txt

# Configura permissões do banco
mkdir -p /var/lib/render/data
touch /var/lib/render/data/arbovirose.db
chmod 666 /var/lib/render/data/arbovirose.db

# Inicia os serviços
cd Arbovirose_streamlit
streamlit run app.py --server.port $PORT &
gunicorn app:health_app -b 0.0.0.0:8081
