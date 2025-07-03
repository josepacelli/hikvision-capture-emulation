#!/bin/bash

# Caminho do ambiente virtual
VENV_PATH="/Users/pacelli/git/pacelli/cam-virtual/fake-camera-lite/venv/bin"

# Exportar variáveis de ambiente
export SIMULADOR_PASS="atl%123operacao"
export SIMULADOR_USER="admin"
export PORT=80

# Executar o aplicativo com Uvicorn
"$VENV_PATH/python" /Users/pacelli/git/pacelli/cam-virtual/fake-camera-lite/main.py --reload --host 0.0.0.0 --port 80