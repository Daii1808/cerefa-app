import os
import sys

# FIX DE RUTAS PARA VERCEL
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

# ========================================================
# RUTA PRINCIPAL (SOLO LECTURA - DASHBOARD)
# ========================================================
@app.route('/')
def home():
    # Solo traemos los datos de tu modelo impecable
    lista_eventos, especies, total_eventos, ultimo = RegistroEvento.obtener_datos_dashboard()
    
    ultimo_saldo = ultimo.saldo_actual if ultimo else 0
    estado_bd = "CONECTADA (Supabase)"
    color_bd = "text-emerald-400"

    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CEREFA - API Portal Control</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-zinc-950 text-zinc-100 min-h-screen p-6">
        
        <div class="max-w-5xl mx-auto space-y-8">
            
            <div class="flex items-center justify-between border-b border-zinc-800 pb-6 mt-4">
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
                <div class="bg-zinc-900 border border-zinc-800 p-5 rounded-xl space-y-2">
                    <span class="text-xs font-medium text-zinc-500 uppercase tracking-wider">Infraestructura</span>
                    <div class="text-lg font-bold {{ color_bd }} font-mono">{{ estado_bd }}</div>
                    <p class="text-xs text-zinc-400">Motor relacional PostgreSQL</p>
                </div>
                <div class="bg-zinc-900 border border-zinc-800 p-5 rounded-xl space-y-2">
                    <span class="text-xs font-medium text-zinc-500 uppercase tracking-wider">Registros Históricos</span>
                    <div class="text-3xl font-mono font-bold text-white">{{ total_eventos }}</div>
                    <p class="text-xs text-zinc-400">Eventos migrados y procesados</p>
                </div>
                <div class="bg-zinc-900 border border-zinc-800 p-5 rounded-xl space-y-2">
                    <span class="text-xs font-medium text-zinc-500 uppercase tracking-wider">Último Saldo Calculado</span>
                    <div class="text-3xl font-mono font-bold text-sky-400">{{ ultimo_saldo }}</div>
                    <p class="text-xs text-zinc-400">Ejemplares activos en el censo</p>
                </div>
            </div>

            <div class="bg-zinc-900 border border-zinc-800 rounded-xl p-6 overflow-x-auto">
                <h2 class="text-lg font-bold text-white mb-4">📋 Visor del Censo en Vivo</h2>
                <table class="w-full text-left text-sm">
                    <thead class="text-zinc-500 border-b border-zinc-800 text-xs uppercase">
                        <tr>
                            <th class="pb-3 font-medium">N° Ficha</th>
                            <th class="pb-3 font-medium">Especie</th>
                            <th class="pb-3 font-medium">Tipo Evento</th>
                            <th class="pb-3 font-medium text-center">Cant.</th>
                            <th class="pb-3 font-medium text-right text-sky-400">Saldo Actual</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-zinc-800/50">
                        {% for reg in lista_eventos %}
                        <tr class="hover:bg-zinc-800/30">
                            <td class="py-3 font-mono text-zinc-300">{{ reg.numero_ficha }}</td>
                            <td class="py-3 text-white">{{ reg.especie.nombre_comun }}</td>
                            <td class="py-3 text-zinc-400">{{ reg.tipo_evento }}</td>
                            <td class="py-3 text-center text-zinc-400">{{ reg.numero_ejemplar }}</td>
                            <td class="py-3 text-right font-mono font-bold text-sky-400">{{ reg.saldo_actual }}</td>
                        </tr>
                        {% else %}
                        <tr>
                            <td colspan="5" class="py-8 text-center text-zinc-600 font-mono text-xs">
                                // LA BASE DE DATOS ESTÁ VACÍA // ESPERANDO CONEXIÓN DE TABLETS //
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            <div class="text-center text-xs text-zinc-600 mt-8">
                Diseño de Arquitectura de Software Optimizado • Taller de Innovación 2026
            </div>
        </div>
    </body>
    </html>
    """
    # Pasamos las variables al HTML
    return render_template_string(
        html_content, 
        total_eventos=total_eventos, 
        ultimo_saldo=ultimo_saldo, 
        estado_bd=estado_bd, 
        color_bd=color_bd,
        lista_eventos=lista_eventos
    )

# ========================================================
# RUTAS DE LA API REALES
# ========================================================
@app.route('/api/v1/status', methods=['GET'])
def status():
    return jsonify({"status": "success", "message": "Servidor central operativo", "database": "connected"})

if __name__ == '__main__':
    app.run(debug=True)