import os
import sys

# FIX DE RUTAS
directorio_actual = os.path.dirname(os.path.abspath(__file__))
carpeta_src = os.path.abspath(os.path.join(directorio_actual, '..'))
if carpeta_src not in sys.path:
    sys.path.insert(0, carpeta_src)

from flask import Flask, request, redirect, url_for, render_template_string
from database.connection import db
from core.models.pacientes import RegistroEvento

app = Flask(__name__)

# CONFIGURACIÓN DE PRODUCCIÓN
database_url = os.environ.get("DATABASE_URL")
if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "connect_args": {"sslmode": "require"},
        "pool_pre_ping": True
    }
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cerefa_local_dev.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

@app.route('/')
def home():
    error_msg = request.args.get('error')
    lista, _, _, _ = RegistroEvento.obtener_datos_dashboard()
    
    html = """
    <!DOCTYPE html>
    <html lang="es"><head><script src="https://cdn.tailwindcss.com"></script></head>
    <body class="bg-zinc-950 text-zinc-100 p-8"><div class="max-w-6xl mx-auto">
        
        {% if error_msg %}
        <div class="bg-rose-950 border border-rose-600 p-4 rounded mb-6 text-rose-200 font-mono text-xs">
            ❌ ERROR DETECTADO: {{ error_msg }}
        </div>
        {% endif %}

        <h1 class="text-2xl font-bold mb-6 border-b border-zinc-800 pb-4">🐾 Panel CEREFA</h1>
        
        <form action="/web/registrar" method="POST" class="grid grid-cols-2 lg:grid-cols-6 gap-4 bg-zinc-900 p-6 rounded-xl border border-zinc-800 mb-8">
            <input type="text" name="numero_ficha" placeholder="Ficha" required class="bg-zinc-950 border border-zinc-700 p-2 rounded text-sm">
            <input type="text" name="numero_acta_movimiento" placeholder="Acta" class="bg-zinc-950 border border-zinc-700 p-2 rounded text-sm">
            <input type="text" name="nombre_comun" placeholder="Especie" required class="bg-zinc-950 border border-zinc-700 p-2 rounded text-sm">
            <input type="text" name="categoria_evento" placeholder="Cat." class="bg-zinc-950 border border-zinc-700 p-2 rounded text-sm">
            <input type="text" name="destino" placeholder="Destino" class="bg-zinc-950 border border-zinc-700 p-2 rounded text-sm">
            <button type="submit" class="bg-emerald-700 hover:bg-emerald-600 font-bold p-2 rounded text-sm">GUARDAR</button>
            <input type="text" name="observacion" placeholder="Observación" class="col-span-2 lg:col-span-6 bg-zinc-950 border border-zinc-700 p-2 rounded text-sm">
            <input type="hidden" name="numero_ejemplar" value="1">
        </form>

        <div class="bg-zinc-900 p-6 rounded-xl border border-zinc-800 overflow-x-auto">
            <table class="w-full text-sm text-left">
                <thead class="text-zinc-500 uppercase border-b border-zinc-800">
                    <tr><th class="py-2">Ficha</th><th class="py-2">Acta</th><th class="py-2">Especie</th><th class="py-2">Cat</th><th class="py-2">Destino</th><th class="py-2">Obs</th></tr>
                </thead>
                <tbody class="divide-y divide-zinc-800">
                    {% for r in lista %}
                    <tr>
                        <td class="py-3 font-mono">{{ r.numero_ficha }}</td>
                        <td class="py-3">{{ r.numero_acta_movimiento or '-' }}</td>
                        <td class="py-3">{{ r.especie.nombre_comun if r.especie else 'N/A' }}</td>
                        <td class="py-3">{{ r.categoria_evento or '-' }}</td>
                        <td class="py-3">{{ r.destino or '-' }}</td>
                        <td class="py-3 text-zinc-400">{{ r.observacion or '-' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>