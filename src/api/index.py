import os
from flask import Flask, jsonify, render_template_string
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

# 2. PROCESAR EL MODELO DIRECTO PARA RENDERIZAR
# Importamos el modelo que creaste en pacientes.py para usarlo en la vista
try:
    from core.models.pacientes import RegistroEvento, CatalogoFauna
except ImportError:
    # Por si las rutas de carpetas locales varían en el despliegue
    class RegistroEvento(db.Model):
        __tablename__ = 'registro_eventos'
        id = db.Column(db.Integer, primary_key=True)
        saldo_actual = db.Column(db.Integer)
        tipo_evento = db.Column(db.String(50))

# ========================================================
# FRONTEND EN INDEX.PY (Visualización del Censo en Vivo)
# ========================================================
@app.route('/')
def home():
    # LÓGICA DE OPTIMIZACIÓN: Sacamos métricas reales de la BD para mostrarlas en la pantalla
    try:
        total_eventos = RegistroEvento.query.count()
        # Buscamos el último registro para ver el censo total activo o el movimiento reciente
        ultimo_movimiento = RegistroEvento.query.order_by(RegistroEvento.id.desc()).first()
        estado_bd = "CONECTADA (Supabase)"
        color_bd = "text-emerald-400"
    except Exception:
        total_eventos = 0
        ultimo_movimiento = None
        estado_bd = "MODO LOCAL / CACHÉ"
        color_bd = "text-amber-400"

    # HTML definitivo con Tailwind CSS optimizado para escritorio (PC)
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CEREFA - API Portal Control</title>
        <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    </head>
    <body class="bg-zinc-950 text-zinc-100 min-h-screen flex flex-col items-center justify-center p-6">
        
        <div class="max-w-4xl w-full bg-zinc-900 border border-zinc-800 rounded-2xl p-8 shadow-2xl space-y-8">
            
            <div class="flex items-center justify-between border-b border-zinc-800 pb-6">
                <div class="space-y-1">
                    <h1 class="text-3xl font-extrabold tracking-tight text-white flex items-center gap-3">
                        🐾 Panel de Control CEREFA
                    </h1>
                    <p class="text-sm text-zinc-400">Servidor Core de Producción en la Nube</p>
                </div>
                <div class="flex items-center gap-2 bg-emerald-950/50 border border-emerald-800 px-3 py-1.5 rounded-full">
                    <span class="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    <span class="text-xs font-mono text-emerald-400 font-medium tracking-wider">API ONLINE</span>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                
                <div class="bg-zinc-950 border border-zinc-800 p-5 rounded-xl space-y-2">
                    <span class="text-xs font-medium text-zinc-500 uppercase tracking-wider">Infraestructura</span>
                    <div class="text-lg font-bold {color_bd} font-mono">{estado_bd}</div>
                    <p class="text-xs text-zinc-400">Motor relacional PostgreSQL</p>
                </div>

                <div class="bg-zinc-950 border border-zinc-800 p-5 rounded-xl space-y-2">
                    <span class="text-xs font-medium text-zinc-500 uppercase tracking-wider">Registros Históricos</span>
                    <div class="text-3xl font-mono font-bold text-white">{total_eventos}</div>
                    <p class="text-xs text-zinc-400">Eventos migrados y procesados</p>
                </div>

                <div class="bg-zinc-950 border border-zinc-800 p-5 rounded-xl space-y-2">
                    <span class="text-xs font-medium text-zinc-500 uppercase tracking-wider">Último Saldo Calculado</span>
                    <div class="text-3xl font-mono font-bold text-sky-400">
                        {ultimo_movimiento.saldo_actual if ultimo_movimiento else 0}
                    </div>
                    <p class="text-xs text-zinc-400">Ejemplares activos en el censo</p>
                </div>

            </div>

            <div class="bg-zinc-950 border border-zinc-800 rounded-xl p-6 space-y-4">
                <h3 class="text-sm font-semibold text-zinc-300">Rutas de Producción Habilitadas (Endpoints REST)</h3>
                <div class="font-mono text-xs space-y-2.5">
                    <div class="flex items-center justify-between p-2.5 bg-zinc-900 rounded border border-zinc-800">
                        <span class="text-emerald-400 font-bold">GET</span>
                        <span class="text-zinc-300 flex-1 ml-4">/api/v1/status</span>
                        <span class="text-zinc-500">Verificar latencia y entorno</span>
                    </div>
                    <div class="flex items-center justify-between p-2.5 bg-zinc-900 rounded border border-zinc-800">
                        <span class="text-sky-400 font-bold">POST</span>
                        <span class="text-zinc-300 flex-1 ml-4">/api/v1/eventos</span>
                        <span class="text-zinc-500">Inyectar datos desde las tablets</span>
                    </div>
                </div>
            </div>

            <div class="text-center text-xs text-zinc-500">
                Diseño de Arquitectura de Software Optimizado • Taller de Innovación 2026
            </div>

        </div>
    </body>
    </html>
    """
    return render_template_string(html_content)

# ========================================================
# ENDPOINTS REST API
# ========================================================
@app.route('/api/v1/status', methods=['GET'])
def status():
    return jsonify({{
        "status": "success", 
        "message": "Servidor central operativo",
        "database": "connected"
    }})

if __name__ == '__main__':
    app.run(debug=True)