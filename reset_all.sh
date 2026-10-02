#!/bin/bash

PROJECT_DIR="$PWD"
cd "$PROJECT_DIR" || exit 1

echo "=== [1/6] Removendo e parando o daemon do systemd (FoxxPI) ==="
if systemctl list-unit-files | grep -q "foxxpi.service"; then
    echo "[+] Parando o serviço foxxpi..."
    sudo systemctl stop foxxpi.service 2>/dev/null
    sudo systemctl disable foxxpi.service 2>/dev/null
    
    if [ -f "/etc/systemd/system/foxxpi.service" ]; then
        echo "[+] Removendo ficheiro de configuração do systemd..."
        sudo rm -f /etc/systemd/system/foxxpi.service
    fi
    
    sudo systemctl daemon-reload
    sudo systemctl reset-failed
    echo "[+] Daemon do systemd removido com sucesso."
else
    echo "[+] Nenhum serviço do systemd 'foxxpi.service' detetado para remover."
fi

echo "=== [2/6] Desativando Tailscale Funnel ==="
if command -v tailscale &> /dev/null; then
    sudo tailscale funnel 5000 off 2>/dev/null
    echo "[+] Tailscale Funnel encerrado."
fi

echo "=== [3/6] Parando processos Python e Scraper órfãos ==="
for porta in 5000 8080; do
    pid=$(lsof -ti tcp:$porta 2>/dev/null)
    if [ -n "$pid" ]; then
        echo "[+] Encerrando processo na porta $porta (PID: $pid)..."
        kill -9 $pid 2>/dev/null
    fi
done
pkill -f "backend/main.py" 2>/dev/null
pkill -f "backend/scraper.py" 2>/dev/null
pkill -f "http.server" 2>/dev/null

echo "=== [4/6] Limpeza profunda de containers, volumes e redes Docker ==="
docker stop foxxpi_mysql_db 2>/dev/null
docker rm -f foxxpi_mysql_db 2>/dev/null
docker volume rm foxxpi_foxxpi_mysql_data 2>/dev/null
docker network prune -f 2>/dev/null

echo "=== [5/6] Removendo notify-send personalizado local ==="
if [ -f "$HOME/.local/bin/notify-send" ]; then
    rm -f "$HOME/.local/bin/notify-send"
    echo "[+] Removido: $HOME/.local/bin/notify-send"
else
    echo "[+] Nenhum notify-send local encontrado para remover."
fi

echo "=== [6/6] Limpando cache do Python e logs locais ==="
find "$PROJECT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find "$PROJECT_DIR" -name "*.pyc" -delete 2>/dev/null
rm -f scraper_cron.log backend.log frontend.log setup_daemon.log cron_system.log

sudo systemctl daemon-reload

echo "=== Ambiente 100% limpo e reestruturado com sucesso! ==="
echo "Próximo passo recomendado: rode o instalador -> ./install_scrapper.sh"