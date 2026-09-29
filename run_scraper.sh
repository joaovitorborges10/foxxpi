#!/bin/bash

# Define o caminho do projeto de forma dinâmica usando o diretório home do usuário
PROJECT_DIR="$HOME/Estudos_Eng_Software/foxxpi"
LOG_FILE="$PROJECT_DIR/scraper_cron.log"

# Garante que o script pare se houver erros e navega até a pasta
cd "$PROJECT_DIR" || exit 1

# Ativa o ambiente virtual
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Registra a data no log
echo "=== Executando Scraper FoxxPI em $(date) ===" >> "$LOG_FILE"

# 1. Inicia o Backend em segundo plano se não estiver ativo
if ! pgrep -f "backend/main.py" > /dev/null; then
    echo "[Cron] Subindo backend/main.py..." >> "$LOG_FILE"
    nohup python3 backend/main.py >> "$PROJECT_DIR/backend.log" 2>&1 &
    # Dá uma margem maior para o backend estabilizar a conexão com o banco
    sleep 5
fi

# 2. Executa o Scraper
python3 backend/scraper.py >> "$LOG_FILE" 2>&1

echo "=== Concluído em $(date) ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
