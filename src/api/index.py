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
# VISTA PRINCIPAL CON FORMULARIO Y TABLA INTEGRADOS
# ========================================================
@app.route('/')
def home():
    # Usamos tu método del modelo pacientes.py para traer la info
    lista_eventos, especies, total_eventos, ultimo = RegistroEvento.obtener_datos_dashboard()
    
    ultimo_saldo = ultimo.saldo_actual if ultimo else 0
    estado_bd = "CONECTADA (Supabase)"
    color_bd = "text-emerald-400"
    
    # Capturamos algún error de validación si es que ocurre (ej: especie no registrada)
    msg_error = request.args.get('error', '')

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
        
        <div class="max-w-7xl mx-auto space-y-8">
            
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

            {% if msg_error %}
            <div class="bg-rose-950/40 border border-rose-900/60 p-4 rounded-xl text-rose-400 text-xs font-mono">
                ⚠️ ERROR EN MODELO: {{ msg_error }}
            </div>
            {% endif %}

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="bg-zinc-900 border border-zinc-800 p-5 rounded-xl space-y-2">
                    <span class="text-xs font-medium text-zinc-500 uppercase tracking-wider">Infraestructura</span>
                    <div class="text-lg font-bold {{ color_bd }} font-mono">{{ estado_bd }}</div>
                </div>
                <div class="bg-zinc-900 border border-zinc-800 p-5 rounded-xl space-y-2">
                    <span class="text-xs font-medium text-zinc-500 uppercase tracking-wider">Registros Históricos</span>
                    <div class="text-3xl font-mono font-bold text-white">{{ total_eventos }}</div>
                </div>
                <div class="bg-zinc-900 border border-zinc-800 p-5 rounded-xl space-y-2">
                    <span class="text-xs font-medium text-zinc-500 uppercase tracking-wider">Último Saldo Calculado</span>
                    <div class="text-3xl font-mono font-bold text-sky-400">{{ ultimo_saldo }}</div>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
                
                <div class="bg-zinc-900 border border-zinc-800 rounded-xl p-6 lg:col-span-1 h-fit shadow-xl">
                    <h2 class="text-lg font-bold text-white mb-4">📝 Agregar Paciente</h2>
                    <form action="/web/registrar" method="POST" class="space-y-4">
                        <div>
                            <label class="block text-xs text-zinc-500 mb-1 font-mono">N° FICHA</label>
                            <input type="text" name="numero_ficha" placeholder="Ej: F-042" required class="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-sm text-white focus:outline-none focus:border-zinc-700">
                        </div>
                        <div>
                            <label class="block text-xs text-zinc-500 mb-1 font-mono">ESPECIE (COMÚN)</label>
                            <input type="text" name="nombre_comun" placeholder="Ej: Pudú" required class="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-sm text-white focus:outline-none focus:border-zinc-700">
                        </div>
                        <div>
                            <label class="block text-xs text-zinc-500 mb-1 font-mono">TIPO EVENTO</label>
                            <select name="tipo_evento" class="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-sm text-white focus:outline-none focus:border-zinc-700">
                                <option value="Ingreso">Ingreso</option>
                                <option value="Egreso">Egreso</option>
                                <option value="Liberación">Liberación</option>
                                <option value="Fallecido">Fallecido</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs text-zinc-500 mb-1 font-mono">CANTIDAD</label>
                            <input type="number" name="numero_ejemplar" value="1" min="1" required class="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-sm text-white focus:outline-none focus:border-zinc-700">
                        </div>
                        <div>
                            <label class="block text-xs text-zinc-500 mb-1 font-mono">OBSERVACIONES</label>
                            <textarea name="observacion" placeholder="Detalles clínicos..." rows="2" class="w-full bg-zinc-950 border border-zinc-800 rounded p-2 text-sm text-white focus:outline-none focus:border-zinc-700"></textarea>
                        </div>
                        <button type="submit" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2.5 rounded text-sm transition-colors cursor-pointer shadow-lg">
                            Guardar en la Nube
                        </button>
                    </form>
                </div>

                <div class="bg-zinc-900 border border-zinc-800 rounded-xl p-6 lg:col-span-3 overflow-x-auto shadow-xl">
                    <h2 class="text-lg font-bold text-white mb-4">📋 Visor del Censo en Vivo</h2>
                    <table class="w-full text-left text-sm whitespace-nowrap">
                        <thead class="text-zinc-500 border-b border-zinc-800 text-xs uppercase">
                            <tr>
                                <th class="pb-3 px-2 font-medium">N° Ficha</th>
                                <th class="pb-3 px-2 font-medium">Especie</th>
                                <th class="pb-3 px-2 font-medium">Tipo Evento</th>
                                <th class="pb-3 px-2 font-medium">Observación</th>
                                <th class="pb-3 px-2 text-center font-medium">Cant.</th>
                                <th class="pb-3 px-2 text-right font-medium text-sky-400">Saldo Actual</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-zinc-800/50">
                            {% for reg in lista_eventos %}
                            <tr class="hover:bg-zinc-800/30 transition-colors">
                                <td class="py-3 px-2 font-mono text-zinc-300">{{ reg.numero_ficha }}</td>
                                <td class="py-3 px-2 text-white">{{ reg.especie.nombre_comun if reg.especie else 'Desconocida' }}</td>
                                <td class="py-3 px-2 text-zinc-400">{{ reg.tipo_evento }}</td>
                                <td class="py-3 px-2 text-zinc-400 truncate max-w-xs" title="{{ reg.observacion }}">{{ reg.observacion or '-' }}</td>
                                <td class="py-3 px-2 text-center text-zinc-400">{{ reg.numero_ejemplar }}</td>
                                <td class="py-3 px-2 text-right font-mono font-bold text-sky-400">{{ reg.saldo_actual }}</td>
                            </tr>
                            {% else %}
                            <tr>
                                <td colspan="6" class="py-8 text-center text-zinc-600 font-mono text-xs">
                                    // NO HAY REGISTROS EN LA NUBE AÚN //
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>

            </div>
            
            <div class="text-center text-xs text-zinc-600 mt-8">
                Diseño de Arquitectura de Software Optimizado • Taller de Innovación 2026
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(
        html_content, total_eventos=total_eventos, ultimo_saldo=ultimo_saldo, 
        estado_bd=estado_bd, color_bd=color_bd, lista_eventos=lista_eventos, msg_error=msg_error
    )

# ========================================================
# PROCESAMIENTO DEL FORMULARIO WEB
# ========================================================
@app.route('/web/registrar', methods=['POST'])
def web_registrar():
    try:
        # Invocamos directamente tu método inteligente de pacientes.py
        RegistroEvento.registrar_con_saldo(
            numero_ficha=request.form.get('numero_ficha'),
            nombre_comun=request.form.get('nombre_comun'),
            tipo_evento=request.form.get('tipo_evento'),
            numero_ejemplar=int(request.form.get('numero_ejemplar', 1)),
            observacion=request.form.get('observacion')
        )
        return redirect(url_for('home'))
    except Exception as e:
        # Si salta un error (ej: la especie no está en el catálogo oficial), recargamos mostrando el error
        return redirect(url_for('home', error=str(e)))

if __name__ == '__main__':
    app.run(debug=True)