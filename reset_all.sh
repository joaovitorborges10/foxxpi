#!/bin/bash

PROJECT_DIR="$PWD"
cd "$PROJECT_DIR" || exit 1

echo "=== [1/4] Parando processos Python nas portas 5000 e 8080 ==="
for porta in 5000 8080; do
    pid=$(lsof -ti tcp:$porta)
    if [ -n "$pid" ]; then
        echo "[+] Encerrando processo na porta $porta (PID: $pid)..."
        kill -9 $pid
    fi
done
pkill -f "backend/main.py"
pkill -f "http.server"

echo "=== [2/4] Destruindo de forma isolada o container e o volume do MySQL do FoxxPI ==="
docker stop foxxpi_mysql_db 2>/dev/null
docker rm -f foxxpi_mysql_db 2>/dev/null
docker volume rm foxxpi_foxxpi_mysql_data 2>/dev/null

echo "=== [3/4] Removendo notify-send personalizado local ==="
if [ -f "$HOME/.local/bin/notify-send" ]; then
    rm -f "$HOME/.local/bin/notify-send"
    echo "[+] Removido: $HOME/.local/bin/notify-send"
else
    echo "[+] Nenhum notify-send local encontrado para remover."
fi

echo "=== [Reset] A limpar o crontab do FoxxPI ==="
crontab -l 2>/dev/null | grep -vE "run_scraper(_full_deploy|_wsl)?\.sh" | crontab -

echo "=== [5/4] Limpando cache do Python (__pycache__) ==="
find "$PROJECT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find "$PROJECT_DIR" -name "*.pyc" -delete 2>/dev/null

echo "=== [4/4] Limpando arquivos de log locais ==="
rm -f scraper_cron.log backend.log frontend.log

echo "=== Reset completo executado! O ambiente está 100% limpo. ==="
echo "Dica: Para reiniciar tudo do zero, basta rodar: ./run_scraper.sh"
