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

# RUTA PRINCIPAL
@app.route('/')
def home():
    lista, _, _, _ = RegistroEvento.obtener_datos_dashboard()
    html = """
    <!DOCTYPE html>
    <html lang="es"><head><script src="https://cdn.tailwindcss.com"></script></head>
    <body class="bg-zinc-950 text-zinc-100 p-8"><div class="max-w-6xl mx-auto">
        <h1 class="text-2xl font-bold mb-6 border-b border-zinc-800 pb-4">🐾 Panel CEREFA: Gestión de Pacientes</h1>
        
        <form action="/web/registrar" method="POST" class="grid grid-cols-2 lg:grid-cols-4 gap-4 bg-zinc-900 p-6 rounded-xl border border-zinc-800 mb-8">
            <input type="text" name="numero_ficha" placeholder="N° Ficha" required class="bg-zinc-950 border border-zinc-700 p-2 rounded text-sm">
            <input type="text" name="numero_acta_movimiento" placeholder="N° Acta" class="bg-zinc-950 border border-zinc-700 p-2 rounded text-sm">
            <input type="text" name="nombre_comun" placeholder="Especie" required class="bg-zinc-950 border border-zinc-700 p-2 rounded text-sm">
            <input type="text" name="categoria_evento" placeholder="Categoría" class="bg-zinc-950 border border-zinc-700 p-2 rounded text-sm">
            <input type="text" name="destino" placeholder="Destino" class="bg-zinc-950 border border-zinc-700 p-2 rounded text-sm">
            <input type="number" name="numero_ejemplar" placeholder="Cant." value="1" required class="bg-zinc-950 border border-zinc-700 p-2 rounded text-sm">
            <input type="text" name="observacion" placeholder="Observación" class="col-span-2 lg:col-span-4 bg-zinc-950 border border-zinc-700 p-2 rounded text-sm">
            <button type="submit" class="col-span-2 lg:col-span-4 bg-emerald-700 hover:bg-emerald-600 font-bold p-2 rounded">GUARDAR REGISTRO</button>
        </form>

        <div class="bg-zinc-900 p-6 rounded-xl border border-zinc-800 overflow-x-auto">
            <table class="w-full text-sm">
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
            </table>
        </div>
    </div></body></html>
    """
    return render_template_string(html, lista=lista)

# RUTA DE REGISTRO
@app.route('/web/registrar', methods=['POST'])
def web_registrar():
    try:
        RegistroEvento.registrar_con_saldo(
            numero_ficha=request.form.get('numero_ficha'),
            numero_acta_movimiento=request.form.get('numero_acta_movimiento'),
            nombre_comun=request.form.get('nombre_comun'),
            categoria_evento=request.form.get('categoria_evento'),
            destino=request.form.get('destino'),
            observacion=request.form.get('observacion'),
            tipo_evento="Ingreso",
            numero_ejemplar=int(request.form.get('numero_ejemplar', 1))
        )
    except Exception as e:
        print(f"Error técnico: {e}")
    return redirect(url_for('home'))

application = app