#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$PROJECT_DIR/setup_daemon.log"
SERVICE_NAME="foxxpi.service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"

CURRENT_USER=$(whoami)
USER_GROUP=$(id -gn)

touch "$PROJECT_DIR/scraper_cron.log"
chown "$CURRENT_USER:$USER_GROUP" "$PROJECT_DIR/scraper_cron.log"
chmod 664 "$PROJECT_DIR/scraper_cron.log"

cd "$PROJECT_DIR" || exit 1

echo "=== [$(date)] Iniciando Setup Global do Daemon Systemd para FoxxPI ===" | tee -a "$LOG_FILE"

echo "Selecione o ambiente de execução para o daemon do FoxxPI:"
echo "1) Linux Padrão (Scraper Standart)"
echo "2) Linux Full (Deploy / Servidor)"
echo "3) Windows Runtime (WSL / Container)"
read -p "Digite a opção desejada [1-3]: " opcao

case $opcao in
    1)
        TARGET_SCRIPT="$PROJECT_DIR/scraper.sh"
        ENV_DESC="Linux Padrão"
        ;;
    2)
        TARGET_SCRIPT="$PROJECT_DIR/scraper_full_deploy.sh"
        ENV_DESC="Linux Full Deploy"
        ;;
    3)
        TARGET_SCRIPT="$PROJECT_DIR/scraper_wsl.sh"
        ENV_DESC="WSL"
        ;;
    *)
        echo "[Erro] Opção inválida. A cancelar setup." | tee -a "$LOG_FILE"
        exit 1
        ;;
esac

if [ ! -f "$TARGET_SCRIPT" ]; then
    echo "[Erro Crítico] O script selecionado não foi encontrado em: $TARGET_SCRIPT" | tee -a "$LOG_FILE"
    exit 1
fi

echo "[Info] Script selecionado para o daemon: $(basename "$TARGET_SCRIPT") ($ENV_DESC)" | tee -a "$LOG_FILE"

chmod +x "$TARGET_SCRIPT"

echo "[Info] A criar a unit do systemd em $SERVICE_PATH com o utilizador $CURRENT_USER..." | tee -a "$LOG_FILE"

sudo bash -c "cat > $SERVICE_PATH" <<EOF
[Unit]
Description=FoxxPI Scraper and Web Services ($ENV_DESC)
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=$CURRENT_USER
Group=$USER_GROUP
WorkingDirectory=$PROJECT_DIR
ExecStart=/bin/bash "$TARGET_SCRIPT"
Restart=on-failure
RestartSec=10
StandardOutput=append:$PROJECT_DIR/scraper_cron.log
StandardError=append:$PROJECT_DIR/scraper_cron.log

[Install]
WantedBy=multi-user.target
EOF

if [ $? -eq 0 ]; then
    echo "[Sucesso] Ficheiro unit do systemd criado com sucesso." | tee -a "$LOG_FILE"
else
    echo "[Erro Crítico] Falha ao criar o ficheiro unit do systemd." | tee -a "$LOG_FILE"
    exit 1
fi

echo "[Info] A recarregar o daemon do systemd..." | tee -a "$LOG_FILE"
sudo systemctl daemon-reload

echo "[Info] A habilitar o serviço para iniciar no boot (enable)..." | tee -a "$LOG_FILE"
sudo systemctl enable "$SERVICE_NAME"

echo "[Info] A iniciar o serviço FoxxPI em background..." | tee -a "$LOG_FILE"
sudo systemctl restart "$SERVICE_NAME"

sleep 2
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "[Sucesso] O daemon do FoxxPI está ativo e a rodar perfeitamente!" | tee -a "$LOG_FILE"
    sudo systemctl status "$SERVICE_NAME" --no-pager | tee -a "$LOG_FILE"
else
    echo "[Aviso] O serviço foi configurado, mas pode ter encontrado um erro ao iniciar. Verifique os logs com: sudo journalctl -u $SERVICE_NAME -n 50" | tee -a "$LOG_FILE"
fi

echo "=== [$(date)] Setup Global Concluído ===" | tee -a "$LOG_FILE"
echo "" >> "$LOG_FILE"