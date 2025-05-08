from flask import Flask, request, jsonify
import face_recognition
import base64, json
import numpy as np
from PIL import Image
from io import BytesIO
import mysql.connector
import os

app = Flask(__name__)

@app.route('/atualizar_rosto', methods=['POST'])
def atualizar_rosto():
    dados = request.get_json()
    nome = dados['nome']
    imagem_base64 = dados['imagem']

    imagem_decodificada = base64.b64decode(imagem_base64.split(',')[1])
    imagem_pil = Image.open(BytesIO(imagem_decodificada))
    imagem_np = np.array(imagem_pil)

    rosto = face_recognition.face_encodings(imagem_np)
    if not rosto:
        return jsonify({'mensagem': 'Nenhum rosto detectado'}), 400

    vetor = json.dumps(rosto[0].tolist())

    # Conecta e atualiza o banco
    db = mysql.connector.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASS"),
        database=os.environ.get("DB_NAME")
    )
    cursor = db.cursor()
    cursor.execute("UPDATE usuarios SET face_descriptor = %s WHERE nome = %s", (vetor, nome))
    db.commit()
    db.close()

    return jsonify({'mensagem': f'Rosto salvo com sucesso para o usuário {nome}'})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)