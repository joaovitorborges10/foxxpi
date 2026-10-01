#!/bin/bash

PROJECT_DIR="$PWD"
cd "$PROJECT_DIR" || exit 1

echo "=== [1/5] Removendo e parando o daemon do systemd (FoxxPI) ==="
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

echo "=== [2/5] Parando processos Python nas portas 5000 e 8080 e o Scraper ==="
for porta in 5000 8080; do
    pid=$(lsof -ti tcp:$porta)
    if [ -n "$pid" ]; then
        echo "[+] Encerrando processo na porta $porta (PID: $pid)..."
        kill -9 $pid
    fi
done
pkill -f "backend/main.py"
pkill -f "backend/scraper.py"
pkill -f "http.server"

echo "=== [3/5] Destruindo de forma isolada o container e o volume do MySQL do FoxxPI ==="
docker stop foxxpi_mysql_db 2>/dev/null
docker rm -f foxxpi_mysql_db 2>/dev/null
docker volume rm foxxpi_foxxpi_mysql_data 2>/dev/null

echo "=== [4/5] Removendo notify-send personalizado local ==="
if [ -f "$HOME/.local/bin/notify-send" ]; then
    rm -f "$HOME/.local/bin/notify-send"
    echo "[+] Removido: $HOME/.local/bin/notify-send"
else
    echo "[+] Nenhum notify-send local encontrado para remover."
fi

echo "=== [5/5] Limpando cache do Python (__pycache__) e logs locais ==="
find "$PROJECT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find "$PROJECT_DIR" -name "*.pyc" -delete 2>/dev/null
rm -f scraper_cron.log backend.log frontend.log

echo "=== Reset completo executado! O ambiente está 100% limpo. ==="
echo "Dica: Para reiniciar tudo do zero, basta rodar: ./run_scraper.sh"