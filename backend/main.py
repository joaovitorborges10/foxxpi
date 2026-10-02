from flask import Flask, jsonify, request
from flask_cors import CORS
from database import obter_conexao

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/api/noticias', methods=['GET'])
def listar_noticias():
    conn = None
    cursor = None
    try:
        relevantes = request.args.get('relevantes')
        categoria = request.args.get('categoria')

        conn = obter_conexao()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM noticias WHERE 1=1"
        params = []

        if relevantes == 'true':
            query += " AND eh_relevante = TRUE"
            
        if categoria:
            query += " AND categoria = %s"
            params.append(categoria)

        query += " ORDER BY data_publicacao DESC, id DESC LIMIT 30"
            
        cursor.execute(query, params)
        noticias = cursor.fetchall()

        return jsonify(noticias)

    except Exception as e:
        print(f"[FoxxPI Erro API]: {e}")
        return jsonify({"erro": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)