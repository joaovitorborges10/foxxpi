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

echo "=== [2/4] Destruindo volumes e containers do MySQL (Reset do Banco) ==="
# Derruba os containers e apaga o volume de dados do Docker (-v)
docker compose down -v --remove-orphans

echo "=== [3/4] Removendo notify-send personalizado local ==="
if [ -f "$HOME/.local/bin/notify-send" ]; then
    rm -f "$HOME/.local/bin/notify-send"
    echo "[+] Removido: $HOME/.local/bin/notify-send"
else
    echo "[+] Nenhum notify-send local encontrado para remover."
fi

echo "=== [4/4] Limpando arquivos de log locais ==="
rm -f scraper_cron.log backend.log frontend.log

echo "=== Reset completo executado! O ambiente está 100% limpo. ==="
echo "Dica: Para reiniciar tudo do zero, basta rodar: ./run_scraper.sh"
