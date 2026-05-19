import os
import sys

# FIX DE RUTAS PARA VERCEL
directorio_actual = os.path.dirname(os.path.abspath(__file__))
carpeta_src = os.path.abspath(os.path.join(directorio_actual, '..'))
if carpeta_src not in sys.path:
    sys.path.insert(0, carpeta_src)

from flask import Flask, jsonify, render_template_string, request, redirect, url_for
from database.connection import db
from core.models.pacientes import RegistroEvento

app = Flask(__name__)

# CONFIGURACIÓN DE PRODUCCIÓN A PRUEBA DE BALAS
database_url = os.environ.get("DATABASE_URL")
if database_url:
    # Corrección de prefijo si viene como postgres://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    
    # FORZAMOS LA CONEXIÓN PARA EVITAR ERRORES DE RED/DNS
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "connect_args": {
            "sslmode": "require",
            "connect_timeout": 10
        },
        "pool_pre_ping": True,
        "pool_recycle": 300
    }
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cerefa_local_dev.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# ========================================================
# RUTA PRINCIPAL (DASHBOARD + FORMULARIO INTEGRADO)
# ========================================================
@app.route('/')
def home():
    try:
        lista_eventos, especies, total_eventos, ultimo = RegistroEvento.obtener_datos_dashboard()
        ultimo_saldo = ultimo.saldo_actual if ultimo else 0
        estado_bd = "CONECTADA (Supabase)"
        color_bd = "text-emerald-400"
    except Exception as e:
        lista_eventos, total_eventos, ultimo_saldo = [], 0, 0
        estado_bd = "ERROR DE CONEXIÓN"
        color_bd = "text-rose-400"

    html_content = """ 
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CEREFA - Portal Control</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-zinc-950 text-zinc-100 min-h-screen p-6">
        <div class="max-w-7xl mx-auto space-y-8">
            <div class="flex items-center justify-between border-b border-zinc-800 pb-6 mt-4">
                <h1 class="text-3xl font-extrabold text-white">🐾 Panel de Control CEREFA</h1>
                <div class="bg-zinc-900 border border-zinc-800 px-3 py-1 rounded-full text-xs font-mono {{ color_bd }}">{{ estado_bd }}</div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="bg-zinc-900 border border-zinc-800 p-5 rounded-xl">
                    <span class="text-xs text-zinc-500 uppercase">Registros Históricos</span>
                    <div class="text-3xl font-bold text-white">{{ total_eventos }}</div>
                </div>
                <div class="bg-zinc-900 border border-zinc-800 p-5 rounded-xl">
                    <span class="text-xs text-zinc-500 uppercase">Último Saldo</span>
                    <div class="text-3xl font-bold text-sky-400">{{ ultimo_saldo }}</div>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
                <div class="bg-zinc-900 border border-zinc-800 rounded-xl p-6 lg:col-span-1">
                    <h2 class="text-lg font-bold text-white mb-4">📝 Agregar Paciente</h2>
                    <form action="/web/registrar" method="POST" class="space-y-3">
                        <input type="text" name="numero_ficha" placeholder="N° Ficha" required class="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-sm text-white">
                        <input type="text" name="nombre_comun" placeholder="Especie" required class="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-sm text-white">
                        <select name="tipo_evento" class="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-sm text-white">
                            <option value="Ingreso">Ingreso</option><option value="Egreso">Egreso</option>
                        </select>
                        <input type="number" name="numero_ejemplar" value="1" required class="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-sm text-white">
                        <button type="submit" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2 rounded text-sm">Guardar</button>
                    </form>
                </div>