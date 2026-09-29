import schedule
import time
from scraper import monitorar_homepage

def executar_rotina():
    print("[FoxxPI Automação] Iniciando varredura agendada...")
    monitorar_homepage()

# Configuração dos intervalos de execução:
# 1. Executa a cada 1 hora
schedule.every(1).hours.do(executar_rotina)

# 2. Outros exemplos de agendamento que você pode usar:
# schedule.every(30).minutes.do(executar_rotina)  # A cada 30 min
# schedule.every().day.at("08:00").do(executar_rotina) # Todo dia às 8h

if __name__ == "__main__":
    print("[FoxxPI Automação] Serviço de agendamento iniciado com sucesso.")
    
    # Faz uma varredura imediata assim que o serviço sobe
    executar_rotina()
    
    # Mantém o script rodando continuamente verificando a agenda
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verifica os agendamentos a cada 60 segundos