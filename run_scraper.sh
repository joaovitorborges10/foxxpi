#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$PROJECT_DIR/scraper_cron.log"
PORTA_WEB=8080
PORTA_BACKEND=5000

export DISPLAY=:0
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
export DBUS_SESSION_BUS_ADDRESS="unix:path=$XDG_RUNTIME_DIR/bus"
export XAUTHORITY="/home/$(whoami)/.Xauthority"

cd "$PROJECT_DIR" || exit 1

if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

echo "=== Executando Inicialização FoxxPI em $(date) ===" | tee -a "$LOG_FILE"

if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    echo "[Init] Instalando dependências do requirements.txt..." | tee -a "$LOG_FILE"
    pip install -r "$PROJECT_DIR/requirements.txt" --break-system-packages >> "$LOG_FILE" 2>&1
    echo "[Init] Dependências verificadas/instaladas com sucesso." | tee -a "$LOG_FILE"
fi

if [ -f "docker-compose.yml" ]; then
    echo "[Init] Verificando e subindo serviços via Docker Compose..." | tee -a "$LOG_FILE"
    docker compose up -d >> "$LOG_FILE" 2>&1
    
    echo "[Init] Aguardando o MySQL inicializar..." | tee -a "$LOG_FILE"
    until docker exec foxxpi_mysql_db mysqladmin ping -h 127.0.0.1 -u root -p'foxxpiroot' --silent 2>/dev/null; do
        sleep 2
    done
    echo "[Init] MySQL respondeu ao ping. Aguardando estabilização da rede..." | tee -a "$LOG_FILE"
    sleep 4
    echo "[Init] MySQL pronto e operacional." | tee -a "$LOG_FILE"
fi

if [ -f "$PROJECT_DIR/foxxpi_database_schema.sql" ]; then
    echo "[Init] Aplicando schema do banco de dados..." | tee -a "$LOG_FILE"
    docker exec -i foxxpi_mysql_db mysql -h 127.0.0.1 -u root -p'foxxpiroot' foxxpi_database < "$PROJECT_DIR/foxxpi_database_schema.sql" >> "$LOG_FILE" 2>&1
    echo "[Init] Schema aplicado com sucesso." | tee -a "$LOG_FILE"
fi

if ! pgrep -f "backend/main.py" > /dev/null; then
    echo "[Init] Subindo backend/main.py..." | tee -a "$LOG_FILE"
    nohup python3 backend/main.py >> "$PROJECT_DIR/backend.log" 2>&1 &
    BACKEND_PID=$!
    sleep 5
    echo "[Init] Backend iniciado com PID: $BACKEND_PID." | tee -a "$LOG_FILE"
else
    echo "[Init] Backend já se encontra ativo." | tee -a "$LOG_FILE"
fi

if ! pgrep -f "http.server $PORTA_WEB" > /dev/null; then
    echo "[Init] Subindo servidor web estático na porta $PORTA_WEB..." | tee -a "$LOG_FILE"
    nohup python3 -m http.server $PORTA_WEB --bind 0.0.0.0 --directory "$PROJECT_DIR/frontend" >> "$PROJECT_DIR/frontend.log" 2>&1 &
    FRONT_PID=$!
    echo "[Init] Frontend iniciado na porta $PORTA_WEB com PID: $FRONT_PID." | tee -a "$LOG_FILE"
else
    echo "[Init] Servidor web do frontend já está ativo." | tee -a "$LOG_FILE"
fi

if ! pgrep -f "backend/scraper.py" > /dev/null; then
    echo "[Init] Subindo scraper.py em loop contínuo..." | tee -a "$LOG_FILE"
    nohup python3 backend/scraper.py >> "$LOG_FILE" 2>&1 &
    SCRAPER_PID=$!
    echo "[Init] Scraper iniciado em background com PID: $SCRAPER_PID." | tee -a "$LOG_FILE"
else
    echo "[Init] Scraper já se encontra ativo." | tee -a "$LOG_FILE"
fi

echo "=== Inicialização concluída em $(date) ===" | tee -a "$LOG_FILE"
echo "" >> "$LOG_FILE"