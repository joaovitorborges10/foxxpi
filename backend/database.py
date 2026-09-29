import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'foxxpiroot',  # Altere para sua senha do container Docker
    'database': 'foxxpi_database'
}

def obter_conexao():
    return mysql.connector.connect(**DB_CONFIG)

def inicializar_banco():
    """Cria o banco de dados e a tabela caso ainda não existam."""
    # Conexão inicial sem especificar banco para poder criá-lo se necessário
    config_sem_db = DB_CONFIG.copy()
    del config_sem_db['database']
    
    conn = mysql.connector.connect(**config_sem_db)
    cursor = conn.cursor()
    
    cursor.execute("CREATE DATABASE IF NOT EXISTS foxxpi_db;")
    cursor.execute("USE foxxpi_db;")
    
    tabela_query = """
    CREATE TABLE IF NOT EXISTS noticias (
        id INT AUTO_INCREMENT PRIMARY KEY,
        titulo VARCHAR(255) NOT NULL,
        link VARCHAR(500) UNIQUE NOT NULL,
        categoria VARCHAR(50) DEFAULT 'Geral',
        eh_relevante BOOLEAN DEFAULT FALSE,
        capturado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(tabela_query)
    conn.commit()
    cursor.close()
    conn.close()
    print("[FoxxPI DB] Banco de dados e tabelas verificados com sucesso.")

if __name__ == "__main__":
    inicializar_banco()