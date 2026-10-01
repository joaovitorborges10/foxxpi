#!/bin/bash

# Define variáveis e caminhos do projeto de forma dinâmica usando o diretório onde o script está localizado
PROJECT_DIR="$PWD"
LOG_FILE="$PROJECT_DIR/scraper_cron.log"
PORTA_WEB=8080
PORTA_BACKEND=5000

# Garante que o script pare se houver erros e navega até a pasta
cd "$PROJECT_DIR" || exit 1

# Registra a data no log e exibe no terminal simultaneamente
echo "=== Executando Scraper FoxxPI em $(date) ===" | tee -a "$LOG_FILE"

# 0. Instalação e configuração automática do notify-send personalizado
LOCAL_BIN_DIR="$HOME/.local/bin"
mkdir -p "$LOCAL_BIN_DIR"

if [ -f "$PROJECT_DIR/bin/notify-send" ]; then
    echo "[Cron] A configurar o notify-send personalizado..." | tee -a "$LOG_FILE"
    cp "$PROJECT_DIR/bin/notify-send" "$LOCAL_BIN_DIR/notify-send"
    chmod +x "$LOCAL_BIN_DIR/notify-send"
    echo "[Cron] notify-send personalizado instalado e com permissões ativas em $LOCAL_BIN_DIR." | tee -a "$LOG_FILE"
fi

# Garante que os binários locais do utilizador tenham prioridade máxima no PATH
export PATH="$HOME/.local/bin:$PATH"

# Ativa o ambiente virtual
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# 1. Instala as dependências do requirements.txt se ele existir
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    echo "[Cron] Instalando dependências do requirements.txt..." | tee -a "$LOG_FILE"
    pip install -r "$PROJECT_DIR/requirements.txt" --break-system-packages >> "$LOG_FILE" 2>&1
    echo "[Cron] Dependências verificadas/instaladas com sucesso." | tee -a "$LOG_FILE"
fi

# 2. Garante que os containers do Docker Compose estão rodando
if [ -f "docker-compose.yml" ]; then
    echo "[Cron] Verificando e subindo serviços via Docker Compose..." | tee -a "$LOG_FILE"
    docker compose up -d >> "$LOG_FILE" 2>&1
    echo "[Cron] Serviços Docker iniciados." | tee -a "$LOG_FILE"
fi

# 3. Aplica o schema principal do banco via container Docker
if [ -f "$PROJECT_DIR/foxxpi_database_schema.sql" ]; then
    echo "[Cron] Aplicando schema do banco de dados..." | tee -a "$LOG_FILE"
    docker exec -i foxxpi_mysql_db mysql -h 127.0.0.1 -u root -p'foxxpiroot' foxxpi_database < "$PROJECT_DIR/foxxpi_database_schema.sql" >> "$LOG_FILE" 2>&1
    echo "[Cron] Schema aplicado com sucesso." | tee -a "$LOG_FILE"
fi

# 4. Aplica o script de autodelete/scheduler via container Docker
if [ -f "$PROJECT_DIR/database_autodelete_cron.sql" ]; then
    echo "[Cron] Aplicando evento de autodelete (scheduler)..." | tee -a "$LOG_FILE"
    docker exec -i foxxpi_mysql_db mysql -h 127.0.0.1 -u root -p'foxxpiroot' foxxpi_database < "$PROJECT_DIR/database_autodelete_cron.sql" >> "$LOG_FILE" 2>&1
    echo "[Cron] Evento de autodelete configurado com sucesso." | tee -a "$LOG_FILE"
fi

# 5. Inicia o Backend em segundo plano se não estiver ativo
if ! pgrep -f "backend/main.py" > /dev/null; then
    echo "[Cron] Subindo backend/main.py..." | tee -a "$LOG_FILE"
    nohup python3 backend/main.py >> "$PROJECT_DIR/backend.log" 2>&1 &
    BACKEND_PID=$!
    sleep 3
    echo "[Cron] Backend iniciado com PID: $BACKEND_PID." | tee -a "$LOG_FILE"
else
    echo "[Cron] Backend já se encontra ativo." | tee -a "$LOG_FILE"
fi

# 6. Inicia o Servidor Web Frontend Local em segundo plano se não estiver ativo
if ! pgrep -f "http.server $PORTA_WEB" > /dev/null; then
    echo "[Cron] Subindo servidor web estático na porta $PORTA_WEB..." | tee -a "$LOG_FILE"
    nohup python3 -m http.server $PORTA_WEB --bind 0.0.0.0 --directory "$PROJECT_DIR/frontend" >> "$PROJECT_DIR/frontend.log" 2>&1 &
    FRONT_PID=$!
    echo "[Cron] Frontend iniciado na porta $PORTA_WEB com PID: $FRONT_PID." | tee -a "$LOG_FILE"
else
    echo "[Cron] Servidor web do frontend já está ativo." | tee -a "$LOG_FILE"
fi

# 7. Executa o Scraper
echo "[Cron] Executando scraper.py..." | tee -a "$LOG_FILE"
python3 backend/scraper.py >> "$LOG_FILE" 2>&1
echo "[Cron] Scraper executado e registado com sucesso." | tee -a "$LOG_FILE"

echo "=== Concluído em $(date) ===" | tee -a "$LOG_FILE"
echo "" >> "$LOG_FILE"
