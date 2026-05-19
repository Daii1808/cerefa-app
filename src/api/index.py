from flask import Flask, jsonify
from src.config.config import Config  # ➔ Apunta a tu carpeta config real
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
    return "¡Backend CEREFA con Arquitectura Modular de Pizarra corriendo en Vercel!"

@app.route('/api/test')
def test():
    return jsonify({
        "status": "online",
        "arquitectura": "N-Capas Estructurada (Real)"
    })

if __name__ == '__main__':
    app.run(debug=True)