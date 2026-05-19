import os
import sys
from flask import Flask, jsonify

# 1. TRUCO DE RUTAS: Le enseña a Python a mirar desde la raíz 'cerefa-app'
# Así el día de mañana tus importaciones de 'src.database' no fallarán.
raiz_proyecto = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if raiz_proyecto not in sys.path:
    sys.path.append(raiz_proyecto)

# 2. INICIALIZAR LA APP DE FLASK
app = Flask(__name__)

# 3. CONFIGURACIÓN FUTURA (Para cuando crees tu base de datos)
# Aquí dejamos el camino listo para tu SQLite original
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['file_db'] = os.path.join(raiz_proyecto, 'src', 'database', 'cerefa.db')


# ==========================================
# RUTAS TEMPORALES DE PRUEBA (Para Vercel)
# ==========================================

@app.route('/')
def home():
    return "¡Backend de CEREFA conectado e indexado correctamente en la raíz!"

@app.route('/api/test')
def test():
    return jsonify({
        "status": "success",
        "message": "El enchufe de Vercel en src/api/index.py está operativo",
        "proyecto": "CEREFA App Gestión"
    })

# ==========================================
# ESPACIO PARA TUS IMPORTACIONES FUTURAS
# ==========================================
# Cuando programes connection.py y routes.py, Vercel los leerá desde aquí:
#
# from src.database.connection import db
# from src.api.routes import api_blueprint
# app.register_blueprint(api_blueprint)


if __name__ == '__main__':
    app.run(debug=True)