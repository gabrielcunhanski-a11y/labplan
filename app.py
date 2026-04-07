import os
import secrets  
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from argon2 import PasswordHasher
from flask_mail import Mail, Message 

load_dotenv() 

app = Flask(__name__)

CORS(app, origins=["http://localhost:5173"]) 


# ---------------- CONFIGURAÇÕES ---------------- #
# Base de Dados
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mailtrap / E-mail (VALORES DIRETOS)
app.config['MAIL_SERVER'] = 'sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '1cd5c941c016ba'  # Mantém as aspas!
app.config['MAIL_PASSWORD'] = 'eba043c96b5d56'  # Mantém as aspas!
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

print("MEU SERVIDOR É:", os.getenv('MAIL_SERVER'))
db = SQLAlchemy(app)
ph = PasswordHasher()
mail = Mail(app) 

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)


@app.route('/usuarios', methods=['POST'])
@limiter.limit("5 per minute") 
def criar_usuario():
    dados = request.json
    try:
        hash_seguro = ph.hash(dados.get('senha'))
        novo = Usuario(email=dados.get('email'), senha_hash=hash_seguro)
        db.session.add(novo)
        db.session.commit()
        return jsonify({"sucesso": True, "mensagem": "Conta criada com sucesso!"})
    except Exception as e:
        return jsonify({"sucesso": False, "mensagem": "Erro ao criar conta (Email já existe?)"}), 400

@app.route('/login', methods=['POST'])
@limiter.limit("10 per minute") 
def login():
    dados = request.json
    user = Usuario.query.filter_by(email=dados.get('email')).first()
    if user:
        try:
            ph.verify(user.senha_hash, dados.get('senha'))
            return jsonify({"sucesso": True, "mensagem": "Bem-vindo!"})
        except: pass
    return jsonify({"sucesso": False, "mensagem": "Credenciais inválidas."}), 401


@app.route('/solicitar-recuperacao', methods=['POST'])
@limiter.limit("3 per hour")
def recuperar():
    email_destino = request.json.get('email')
    codigo = str(secrets.randbelow(899999) + 100000)
    
    try:
       
        msg = Message(
            subject="LABPLAN - Código de Recuperação",
            sender="noreply@labplan.com",
            recipients=[email_destino]
        )
        msg.body = f"Olá! O seu código de recuperação de acesso ao LABPLAN é: {codigo}. Este código expira em 5 minutos."
        
        mail.send(msg)
        print(f"[LOG] E-mail enviado com sucesso para {email_destino}!")
        return jsonify({"sucesso": True, "mensagem": "Se o e-mail existir, você receberá um código em instantes."})
    
    except Exception as e:
        print(f"[ERRO CRÍTICO] Falha ao enviar e-mail: {e}")
        return jsonify({"sucesso": False, "mensagem": "Erro técnico ao enviar e-mail."}), 500

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode)