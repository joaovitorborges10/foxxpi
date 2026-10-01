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
pkill -f "backend/scraper.py"
pkill -f "http.server"

# Desativa o Tailscale Funnel caso esteja ativo na porta 5000
if command -v tailscale &> /dev/null; then
    if sudo tailscale funnel status 2>&1 | grep -q "5000"; then
        echo "[+] Desativando Tailscale Funnel na porta 5000..."
        sudo tailscale funnel --off 5000 >> /dev/null 2>&1
        echo "[+] Tailscale Funnel desativado."
    else
        echo "[-] Tailscale Funnel não estava ativo na porta 5000."
    fi
fi

echo "=== Serviços interrompidos com sucesso! ==="