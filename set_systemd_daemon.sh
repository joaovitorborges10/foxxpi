#!/bin/bash

# Pega o utilizador atual e o caminho absoluto do diretório atual
CURRENT_USER=$(whoami)
CURRENT_DIR=$(pwd)
PYTHON_PATH=$(which python3)

echo "[*] A configurar o FoxxPI para o utilizador: $CURRENT_USER"
echo "[*] Diretório detetado: $CURRENT_DIR"

# Lógica de prioridade: O padrão é o run_scraper.sh, mas adapta-se se houver outro ativo/presente
SCRIPT_ALVO=""

if [ -f "$CURRENT_DIR/run_scraper.sh" ]; then
    SCRIPT_ALVO="$CURRENT_DIR/run_scraper.sh"
    echo "[+] Padrão aplicado: run_scraper.sh"
elif [ -f "$CURRENT_DIR/run_scraper_full_deploy.sh" ]; then
    SCRIPT_ALVO="$CURRENT_DIR/run_scraper_full_deploy.sh"
    echo "[+] Adaptado para: run_scraper_full_deploy.sh"
elif [ -f "$CURRENT_DIR/run_scraper_wsl.sh" ]; then
    SCRIPT_ALVO="$CURRENT_DIR/run_scraper_wsl.sh"
    echo "[+] Adaptado para: run_scraper_wsl.sh"
else
    # Fallback caso nenhum wrapper exista na pasta
    SCRIPT_ALVO="$CURRENT_DIR/scrapper.py"
    echo "[!] Nenhum wrapper encontrado. A apontar diretamente para: scrapper.py"
fi

# Define o comando de execução no systemd de acordo com a extensão do alvo
if [[ "$SCRIPT_ALVO" == *.sh ]]; then
    EXEC_COMMAND="/bin/bash $SCRIPT_ALVO"
else
    EXEC_COMMAND="$PYTHON_PATH $SCRIPT_ALVO"
fi

# Cria o ficheiro de serviço do systemd de forma dinâmica
sudo bash -c "cat > /etc/systemd/system/foxxpi.service" <<EOF
[Unit]
Description=FoxxPI - UniEVANGELICA News Scraper Agent
After=network.target docker.service mysql.service
Wants=docker.service mysql.service

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
ExecStart=$EXEC_COMMAND
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Recarrega, ativa e inicia o serviço no systemd
sudo systemctl daemon-reload
sudo systemctl enable foxxpi.service
sudo systemctl restart foxxpi.service

echo "[+] FoxxPI configurado com sucesso e a rodar em background!"
sudo systemctl status foxxpi.service --no-pager