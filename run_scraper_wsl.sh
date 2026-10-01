#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$PROJECT_DIR/scraper_cron.log"
PORTA_WEB=8080
PORTA_BACKEND=5000

cd "$PROJECT_DIR" || exit 1

if ! pidof systemd >/dev/null 2>&1; then
    echo "[Erro Crítico] O systemd não está ativado neste ambiente WSL." | tee -a "$LOG_FILE"
    echo "Para habilitar o systemd, edite ou crie o ficheiro /etc/wsl.conf com o seguinte conteúdo:" | tee -a "$LOG_FILE"
    echo -e "[boot]\nsystemd=true" | tee -a "$LOG_FILE"
    echo "Depois, abra o PowerShell no Windows e execute 'wsl --shutdown', reabra o WSL e tente novamente." | tee -a "$LOG_FILE"
    exit 1
fi

echo "=== Executando Inicialização WSL FoxxPI em $(date) ===" | tee -a "$LOG_FILE"

LOCAL_BIN_DIR="$HOME/.local/bin"
mkdir -p "$LOCAL_BIN_DIR"

if [ -f "$PROJECT_DIR/bin/notify-send" ]; then
    echo "[Init] A configurar o notify-send personalizado..." | tee -a "$LOG_FILE"
    cp "$PROJECT_DIR/bin/notify-send" "$LOCAL_BIN_DIR/notify-send"
    chmod +x "$LOCAL_BIN_DIR/notify-send"
    echo "[Init] notify-send personalizado instalado e com permissões ativas em $LOCAL_BIN_DIR." | tee -a "$LOG_FILE"
fi

export PATH="$HOME/.local/bin:$PATH"

if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

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
    sleep 3
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
    echo "[Init] Scraper iniciado e rodando em foreground." | tee -a "$LOG_FILE"
    python3 backend/scraper.py >> "$LOG_FILE" 2>&1
else
    echo "[Init] Scraper já se encontra ativo." | tee -a "$LOG_FILE"
fi

echo "=== Concluído em $(date) ===" | tee -a "$LOG_FILE"
echo "" >> "$LOG_FILE"