import os
import sys

# ========================================================
# 🚀 FIX DE RUTAS PARA VERCEL
# Le decimos a la nube que incluya la carpeta 'src' en su radar
# para que encuentre tus carpetas 'database' y 'core'.
# ========================================================
directorio_actual = os.path.dirname(os.path.abspath(__file__))
carpeta_src = os.path.abspath(os.path.join(directorio_actual, '..'))
if carpeta_src not in sys.path:
    sys.path.insert(0, carpeta_src)

from flask import Flask, jsonify, render_template_string
from database.connection import db
from core.models.pacientes import RegistroEvento

app = Flask(__name__)

# CONFIGURACIÓN DE BASE DE DATOS
database_url = os.environ.get("DATABASE_URL")
if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cerefa_local_dev.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

@app.route('/')
def home():
    # 🚀 Llamamos a TU función del modelo pacientes.py
    lista_eventos, especies, total_eventos, ultimo = RegistroEvento.obtener_datos_dashboard()
    
    # Adaptamos los datos para pintar en el HTML
    ultimo_saldo = ultimo.saldo_actual if ultimo else 0
    estado_bd = "CONECTADA (Supabase)"
    color_bd = "text-emerald-400"

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
                        {ultimo_saldo}
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
                        <span class="text-zinc-500">Verificar latencia y