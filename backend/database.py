import time
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'foxxpiroot',
    'database': 'foxxpi_database',
    'connect_timeout': 10
}

def obter_conexao(tentativas=3, espera=2):
    for i in range(tentativas):
        try:
            return mysql.connector.connect(**DB_CONFIG)
        except mysql.connector.Error as err:
            if i == tentativas - 1:
                raise err
            print(f"[FoxxPI DB] Tentativa {i + 1} de conexão falhou. Tentando novamente em {espera}s...")
            time.sleep(espera)

def inicializar_banco():
    config_sem_db = DB_CONFIG.copy()
    del config_sem_db['database']
    
    conn = None
    cursor = None
    
    try:
        for i in range(3):
            try:
                conn = mysql.connector.connect(**config_sem_db)
                break
            except mysql.connector.Error as err:
                if i == 2:
                    raise err
                time.sleep(2)

        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']};")
        cursor.execute(f"USE {DB_CONFIG['database']};")
        
        tabela_query = """
        CREATE TABLE IF NOT EXISTS noticias (
            id INT AUTO_INCREMENT PRIMARY KEY,
            titulo VARCHAR(255) NOT NULL,
            link VARCHAR(500) UNIQUE NOT NULL,
            categoria VARCHAR(50) DEFAULT 'Geral',
            eh_relevante BOOLEAN DEFAULT FALSE,
            data_publicacao VARCHAR(50) NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(tabela_query)
        conn.commit()
        print("[FoxxPI DB] Banco de dados e tabelas verificados com sucesso.")
        
    except mysql.connector.Error as err:
        print(f"[FoxxPI DB] Erro ao inicializar o banco: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    inicializar_banco()