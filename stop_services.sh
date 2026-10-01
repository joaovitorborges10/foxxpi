#!/bin/bash

echo "=== Parando serviços do FoxxPI nas portas 5000 e 8080 ==="

for porta in 5000 8080; do
    pid=$(lsof -ti tcp:$porta)
    if [ -n "$pid" ]; then
        echo "[+] Encerrando processo na porta $porta (PID: $pid)..."
        kill -9 $pid
    else
        echo "[-] Nenhum processo ativo encontrado na porta $porta."
    fi
done

pkill -f "backend/main.py"
pkill -f "http.server"

echo "=== Serviços interrompidos com sucesso! ==="
