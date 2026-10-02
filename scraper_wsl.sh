#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$PROJECT_DIR/scraper_cron.log"
PORTA_WEB=8080
PORTA_BACKEND=5000

cd "$PROJECT_DIR" || exit 1

if ! pidof systemd >/dev/null 2>&1; then
    echo "[Erro Crítico] O systemd não está ativado neste ambiente WSL." | tee -a "$LOG_FILE"
    echo "Para habilitar, crie o ficheiro /etc/wsl.conf com o conteúdo:" | tee -a "$LOG_FILE"
    echo -e "[boot]\nsystemd=true" | tee -a "$LOG_FILE"
    echo "Depois, execute 'wsl --shutdown' no PowerShell e reabra o WSL." | tee -a "$LOG_FILE"
    exit 1
fi

export DISPLAY=:0
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
export DBUS_SESSION_BUS_ADDRESS="unix:path=$XDG_RUNTIME_DIR/bus"
export XAUTHORITY="/home/$(whoami)/.Xauthority"

echo "=== Executando Inicialização FoxxPI (WSL) em $(date) ===" | tee -a "$LOG_FILE"

LOCAL_BIN_DIR="$HOME/.local/bin"
mkdir -p "$LOCAL_BIN_DIR"

if [ -f "$PROJECT_DIR/bin/notify-send" ]; then
    cp "$PROJECT_DIR/bin/notify-send" "$LOCAL_BIN_DIR/notify-send"
    chmod +x "$LOCAL_BIN_DIR/notify-send"
fi

export PATH="$HOME/.local/bin:$PATH"

if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    pip install -r "$PROJECT_DIR/requirements.txt" --break-system-packages >> "$LOG_FILE" 2>&1
fi

echo "[Init] Aguardando o Docker Daemon responder..." | tee -a "$LOG_FILE"
until docker info >/dev/null 2>&1; do
    sleep 2
done
echo "[Init] Docker Daemon online." | tee -a "$LOG_FILE"

if [ -f "docker-compose.yml" ]; then
    echo "[Init] A descarregar imagens (pull) e subindo serviços via Docker Compose..." | tee -a "$LOG_FILE"
    docker compose pull >> "$LOG_FILE" 2>&1
    docker compose up -d >> "$LOG_FILE" 2>&1
    
    echo "[Init] Aguardando o MySQL inicializar..." | tee -a "$LOG_FILE"
    until docker exec foxxpi_mysql_db mysqladmin ping -h 127.0.0.1 -u root -p'foxxpiroot' --silent 2>/dev/null; do
        sleep 3
    done
    echo "[Init] MySQL pronto e operacional." | tee -a "$LOG_FILE"
else
    echo "[Aviso] docker-compose.yml não encontrado, pulando Docker." | tee -a "$LOG_FILE"
fi

if [ -f "$PROJECT_DIR/foxxpi_database_schema.sql" ]; then
    docker exec -i foxxpi_mysql_db mysql -h 127.0.0.1 -u root -p'foxxpiroot' foxxpi_database < "$PROJECT_DIR/foxxpi_database_schema.sql" >> "$LOG_FILE" 2>&1
fi

if ! pgrep -f "backend/main.py" > /dev/null; then
    nohup python3 backend/main.py >> "$PROJECT_DIR/backend.log" 2>&1 &
    sleep 3
fi

if ! pgrep -f "http.server $PORTA_WEB" > /dev/null; then
    nohup python3 -m http.server $PORTA_WEB --bind 0.0.0.0 --directory "$PROJECT_DIR/frontend" >> "$PROJECT_DIR/frontend.log" 2>&1 &
fi

if ! pgrep -f "backend/scraper.py" > /dev/null; then
    python3 backend/scraper.py >> "$LOG_FILE" 2>&1
fi

echo "=== Inicialização Concluída em $(date) ===" | tee -a "$LOG_FILE"
echo "" >> "$LOG_FILE"