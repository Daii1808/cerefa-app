import os
import sys

# El truco maestro va en la línea 1 y 2 para que arregle el mapa ANTES de importar nada
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from flask import Flask, jsonify
from src.config.config import Config
from src.database.models import db
from src.api.routes.fauna import fauna_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(fauna_bp)

@app.route('/')
def home():
    return "¡Backend CEREFA corriendo impecable!"

@app.route('/api/test')
def test():
    return jsonify({
        "status": "online",
        "arquitectura": "N-Capas Estructurada"
    })

if __name__ == '__main__':
    app.run(debug=True)