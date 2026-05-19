import os
import sys

# FIX DE RUTAS
directorio_actual = os.path.dirname(os.path.abspath(__file__))
carpeta_src = os.path.abspath(os.path.join(directorio_actual, '..'))
if carpeta_src not in sys.path:
    sys.path.insert(0, carpeta_src)

from flask import Flask, jsonify, render_template_string, request, redirect, url_for

# DECLARACIÓN EXPLÍCITA DE LA VARIABLE QUE VERCEL BUSCA
app = Flask(__name__)

from database.connection import db
from core.models.pacientes import RegistroEvento

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

# ========================================================
# RUTA PRINCIPAL
# ========================================================
@app.route('/')
def home():
    try:
        lista_eventos, especies, total_eventos, ultimo = RegistroEvento.obtener_datos_dashboard()
        ultimo_saldo = ultimo.saldo_actual if ultimo else 0
        estado_bd = "CONECTADA (Supabase)"
    except Exception:
        lista_eventos, total_eventos, ultimo_saldo = [], 0, 0
        estado_bd = "ERROR CONEXIÓN"

    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-zinc-950 text-white p-6">
        <div class="max-w-4xl mx-auto">
            <h1 class="text-3xl font-bold mb-6">🐾 Panel CEREFA</h1>
            <div class="bg-zinc-900 p-6 rounded-xl border border-zinc-800">
                <p class="mb-4 text-emerald-400">{{ estado_bd }}</p>
                <div class="grid grid-cols-2 gap-4 mb-8">
                    <div class="bg-zinc-800 p-4 rounded">Registros: {{ total_eventos }}</div>
                    <div class="bg-zinc-800 p-4 rounded">Saldo: {{ ultimo_saldo }}</div>
                </div>
                
                <form action="/web/registrar" method="POST" class="flex gap-2 mb-8">
                    <input type="text" name="numero_ficha" placeholder="Ficha" class="bg-zinc-950 border p-2 rounded w-full">
                    <input type="text" name="nombre_comun" placeholder="Especie" class="bg-zinc-950 border p-2 rounded w-full">
                    <button type="submit" class="bg-emerald-600 px-4 py-2 rounded">Guardar</button>
                </form>

                <table class="w-full text-sm">
                    <thead><tr class="border-b border-zinc-800"><th class="text-left py-2">Ficha</th><th class="text-left py-2">Especie</th></tr></thead>
                    <tbody>
                        {% for reg in lista_eventos %}
                        <tr class="border-b border-zinc-800"><td class="py-2">{{ reg.numero_ficha }}</td><td class="py-2">{{ reg.especie.nombre_comun }}</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_content, total_eventos=total_eventos, ultimo_saldo=ultimo_saldo, estado_bd=estado_bd, lista_eventos=lista_eventos)

@app.route('/web/registrar', methods=['POST'])
def web_registrar():
    try:
        RegistroEvento.registrar_con_saldo(
            numero_ficha=request.form.get('numero_ficha'),
            nombre_comun=request.form.get('nombre_comun'),
            tipo_evento="Ingreso",
            numero_ejemplar=1
        )
    except: pass
    return redirect(url_for('home'))

# Esta línea es para que Vercel sepa qué ejecutar
application = app