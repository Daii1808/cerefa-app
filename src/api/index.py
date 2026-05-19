import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 1. SOLUCIÓN AL ERROR 500: Usar PostgreSQL en producción y SQLite solo como respaldo local
database_url = os.environ.get("DATABASE_URL")

if database_url:
    # Vercel/Supabase a veces usan 'postgres://', pero SQLAlchemy pide 'postgresql://' obligatoriamente
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    # Respaldo para cuando ejecutes el backend local en tu PC
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cerefa_local_dev.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializar la base de datos con la app
db = SQLAlchemy(app)

# ==========================================
# AQUÍ VAN TUS MODELOS (Ej: clase Animal, etc.)
# ==========================================

# 2. SOLUCIÓN A LA LÍNEA 18: Crear las tablas de forma segura en el contexto correcto
with app.app_context():
    try:
        db.create_all()
        print("¡Base de datos sincronizada con éxito en el servidor!")
    except Exception as e:
        print(f"Aviso: No se pudo escribir en el disco local (Esperado en Serverless): {e}")

# ==========================================
# AQUÍ ABAJO SIGUEN TUS RUTAS (@app.route)
# ==========================================
@app.route('/')
def home():
    return {"status": "success", "message": "Backend de CEREFA online en la nube"}

# Esto permite correrlo local con python src/api/index.py
if __name__ == '__main__':
    app.run(debug=True)