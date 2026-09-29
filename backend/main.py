from flask import Flask, jsonify, request
from flask_cors import CORS
from database import obter_conexao

app = Flask(__name__)
CORS(app)  # Libera o acesso para o JavaScript

@app.route('/api/noticias', methods=['GET'])
def listar_noticias():
    try:
        relevantes = request.args.get('relevantes')
        categoria = request.args.get('categoria')

        conn = obter_conexao()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM noticias WHERE 1=1"
        params = []

        if relevantes == 'true':
            query += " AND eh_relevante = TRUE"
        elif categoria:
            query += " AND categoria = %s"
            params.append(categoria)

        query += " ORDER BY id DESC LIMIT 30"
        
        cursor.execute(query, params)
        noticias = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(noticias)
    except Exception as e:
        print(f"[FoxxPI Erro API]: {e}")
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    # Sobe o servidor no IP 0.0.0.0 (acessível de dentro do WSL e do Windows)
    app.run(host='0.0.0.0', port=5000, debug=True)