#!/bin/bash

# Inicializar Backend

python3 ~/foxxpi/backend/main.py

# Caminho absoluto para a pasta do projeto
PROJECT_DIR="/home/joao/foxxpi"
LOG_FILE="$PROJECT_DIR/scraper_cron.log"

# Navega até o diretório do projeto
cd $PROJECT_DIR

# Ativa o ambiente virtual Python e roda o scraper
# (Troca 'venv' pelo nome da tua pasta de ambiente virtual se for diferente)
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Regista a data de execução e roda o scraper
echo "=== Executando Scraper FoxxPI em $(date) ===" >> $LOG_FILE
python3 backend/scraper.py >> $LOG_FILE 2>&1
echo "=== Concluído em $(date) ===" >> $LOG_FILE
