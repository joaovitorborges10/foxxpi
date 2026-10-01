import schedule
import time
from scraper import monitorar_homepage

def executar_rotina():
    print("[FoxxPI Automação] Iniciando varredura agendada...")
    monitorar_homepage()

schedule.every(1).hours.do(executar_rotina)

if __name__ == "__main__":
    print("[FoxxPI Automação] Serviço de agendamento iniciado com sucesso.")
    executar_rotina()
    
    while True:
        schedule.run_pending()
        time.sleep(60)