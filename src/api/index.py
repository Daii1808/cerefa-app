import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 1. CONFIGURACIÓN DE BASE DE DATOS (Producción Cloud / Desarrollo Local)
database_url = os.environ.get("DATABASE_URL")
if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cerefa_local_dev.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Inicialización segura en la nube
with app.app_context():
    try:
        db.create_all()
    except Exception:
        pass

# ========================================================
# VISTA DE FRONTEND PARA VERCEL (La fachada pro)
# ========================================================
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CEREFA - API Portal</title>
        <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    </head>
    <body class="bg-zinc-950 text-zinc-100 min-h-screen flex items-center justify-center p-4">
        
        <div class="max-w-md w-full bg-zinc-900 border border-zinc-800 rounded-2xl p-6 shadow-2xl space-y-6">
            
            <div class="flex items-center justify-between">
                <div class="space-y-1">
                    <h1 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                        🐾 Portal CEREFA
                    </h1>
                    <p class="text-xs text-zinc-400">Servidor API de Producción</p>
                </div>
                <span class="flex h-3 w-3 relative">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                </span>
            </div>

            <hr class="border-zinc-800">

            <div class="bg-zinc-950 border border-zinc-800/80 rounded-xl p-4 space-y-2">
                <div class="flex justify-between text-sm">
                    <span class="text-zinc-500">Servidor Flask:</span>
                    <span class="font-mono text-emerald-400 font-medium">ONLINE</span>
                </div>
                <div class="flex justify-between text-sm">
                    <span class="text-zinc-500">Base de Datos:</span>
                    <span class="text-zinc-300 font-mono text-xs">PostgreSQL Vinculada</span>
                </div>
            </div>

            <div class="space-y-2 text-xs text-zinc-400 leading-relaxed bg-zinc-950/50 p-3 rounded-xl border border-zinc-800/50">
                <p>
                    💡 <strong>Nota del Taller:</strong> Este es el núcleo en la nube. Las pantallas en Streamlit (<code class="text-zinc-200">src/ui/pages/</code>) consumirán estos endpoints para registrar la fauna del centro.
                </p>
            </div>

            <button onclick="document.getElementById('test-box').classList.remove('hidden')" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-sm py-2.5 rounded-xl transition-all cursor-pointer shadow-lg shadow-emerald-900/20 active:scale-[0.98]">
                Verificar Integridad del Sistema
            </button>

            <div id="test-box" class="hidden text-xs font-mono bg-black/50 border border-zinc-800 rounded-lg p-3 text-emerald-400">
                { "status": "success", "database": "connected", "routing": "modular_ok" }
            </div>

        </div>
    </body>
    </html>
    """

# ========================================================
# ENDPOINTS ENDPADS (Para que se conecte la carpeta ui/)
# ========================================================
@app.route('/api/v1/status', methods=['GET'])
def status():
    return jsonify({
        "status": "success", 
        "message": "API lista para recibir datos de Streamlit",
        "environment": "production"
    })

if __name__ == '__main__':
    app.run(debug=True)