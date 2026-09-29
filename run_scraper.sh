#!/bin/bash

# Define o caminho do projeto de forma dinâmica usando o diretório home do usuário
PROJECT_DIR="$HOME/foxxpi"
LOG_FILE="$PROJECT_DIR/scraper_cron.log"

# Garante que o script pare se houver erros graves e navega até a pasta
cd "$PROJECT_DIR" || exit 1

# Ativa o ambiente virtual primeiro para garantir o uso das dependências corretas
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Registra a data no log
echo "=== Executando Scraper FoxxPI em $(date) ===" >> "$LOG_FILE"

# 1. Inicia o Backend em SEGUNDO PLANO (&) se ele não estiver rodando
# O nohup garante que o processo continue e o & libera o terminal para o scraper rodar
if ! pgrep -f "backend/main.py" > /dev/null; then
    nohup python3 backend/main.py >> "$PROJECT_DIR/backend.log" 2>&1 &
    # Aguarda 3 segundos para garantir que o backend subiu antes do scraper iniciar
    sleep 3
fi

# 2. Executa o Scraper e redireciona saídas para o log
python3 backend/scraper.py >> "$LOG_FILE" 2>&1

echo "=== Concluído em $(date) ===" >> "$LOG_FILE"
