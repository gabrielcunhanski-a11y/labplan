from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from argon2 import PasswordHasher
import redis
import random

app = Flask(__name__)
CORS(app)
ph = PasswordHasher() 


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://utilizador:senha@localhost/labplan'
db = SQLAlchemy(app)


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

@app.route('/usuarios', methods=['POST'])
def criar_usuario():
    dados = request.json
    #vlw cerqueira
    hash_seguro = ph.hash(dados.get('senha'))
    novo = Usuario(email=dados.get('email'), senha_hash=hash_seguro)
    db.session.add(novo)
    db.session.commit()
    return jsonify({"sucesso": True, "mensagem": "Conta criada com Argon2!"})

@app.route('/login', methods=['POST'])
def login():
    dados = request.json
    user = Usuario.query.filter_by(email=dados.get('email')).first()
    if user:
        try:
        
            ph.verify(user.senha_hash, dados.get('senha'))
            return jsonify({"sucesso": True, "mensagem": "Bem-vindo!"})
        except:
            pass
    return jsonify({"sucesso": False, "mensagem": "Email ou senha incorretos."})

@app.route('/solicitar-recuperacao', methods=['POST'])
def recuperar():
    email = request.json.get('email')
    codigo = str(random.randint(100000, 999999))
    r.setex(f"recuperar:{email}", 300, codigo) 
    print(f"--- CÓDIGO PARA {email}: {codigo} ---")
    return jsonify({"sucesso": True, "mensagem": "Código enviado (veja o terminal)!"})

@app.route('/usuarios', methods=['GET'])
def listar():
    users = Usuario.query.all()
    return jsonify([{"id": u.id, "email": u.email} for u in users])

if __name__ == '__main__':
    with app.app_context(): db.create_all()
    app.run(debug=True)
