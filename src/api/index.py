import sys
import os
import requests
import datetime

# Agregamos la raíz del proyecto al path
proyecto_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if proyecto_raiz not in sys.path:
    sys.path.insert(0, proyecto_raiz)

from flask import Flask, render_template_string, request, redirect, url_for
from src.config.app import app

def get_supabase_headers():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise Exception(f"Faltan credenciales: URL={bool(url)}, KEY={bool(key)}")
    return url, {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

@app.route('/')
def index():
    error_msg = request.args.get('error')
    exito_msg = request.args.get('exito')
    
    try:
        url, headers = get_supabase_headers()
        # Obtener los ultimos 50 registros, ordenados por los más nuevos primero
        response = requests.get(f"{url}/rest/v1/registro_evento?select=*&order=created_at.desc&limit=50", headers=headers)
        if response.status_code == 200:
            lista = response.json()
        else:
            raise Exception(f"Error de Supabase: {response.text}")
    except Exception as e:
        lista = []
        if not error_msg:
            error_msg = f"Error al cargar BD: {str(e)}"

    html = """
    <!DOCTYPE html>
    <html lang="es"><head><script src="https://cdn.tailwindcss.com"></script></head>
    <body class="bg-zinc-950 text-white p-4 md:p-8">
    <div class="max-w-7xl mx-auto">
        <div class="flex justify-between items-center mb-6">
            <h1 class="text-3xl font-bold">🐾 Panel de Control CEREFA</h1>
            
            <!-- Botón PDF (Visual/Placeholder por petición del usuario) -->
            <button onclick="alert('Esta función exportará los datos a PDF próximamente.')" class="bg-red-700 hover:bg-red-600 text-white font-bold py-2 px-4 rounded-lg flex items-center transition-colors">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                Exportar PDF
            </button>
        </div>
        
        {% if error_msg %}
        <div class="bg-rose-900 p-4 mb-4 rounded-lg text-sm font-mono border border-rose-700 shadow-lg">❌ ERROR: {{ error_msg }}</div>
        {% endif %}
        
        {% if exito_msg %}
        <div class="bg-emerald-900 p-4 mb-4 rounded-lg text-sm font-mono border border-emerald-700 shadow-lg">✅ ÉXITO: {{ exito_msg }}</div>
        {% endif %}

        <!-- FORMULARIO OPTIMIZADO -->
        <form action="/web/registrar" method="POST" class="bg-zinc-900 p-6 rounded-xl border border-zinc-800 mb-8 shadow-xl">
            <h2 class="text-xl text-zinc-400 mb-4 border-b border-zinc-800 pb-2">Nuevo Evento</h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                
                <!-- Columna 1: Tipo de Evento (Botones) -->
                <div class="lg:col-span-1 space-y-2">
                    <label class="text-xs text-zinc-500 uppercase font-bold tracking-wider">Tipo de Evento</label>
                    <div class="flex gap-2">
                        <label class="flex-1 cursor-pointer">
                            <input type="radio" name="tipo_evento" value="Ingreso" class="peer sr-only" checked>
                            <div class="text-center bg-zinc-950 border border-zinc-700 text-zinc-400 p-3 rounded-lg peer-checked:bg-emerald-800 peer-checked:text-emerald-100 peer-checked:border-emerald-500 transition-all font-bold">
                                + Ingreso
                            </div>
                        </label>
                        <label class="flex-1 cursor-pointer">
                            <input type="radio" name="tipo_evento" value="Egreso" class="peer sr-only">
                            <div class="text-center bg-zinc-950 border border-zinc-700 text-zinc-400 p-3 rounded-lg peer-checked:bg-orange-800 peer-checked:text-orange-100 peer-checked:border-orange-500 transition-all font-bold">
                                - Egreso
                            </div>
                        </label>
                    </div>
                </div>

                <!-- Columna 2: Especie -->
                <div class="lg:col-span-2 space-y-2 grid grid-cols-2 gap-4">
                    <div class="col-span-2 md:col-span-1 flex flex-col justify-end">
                        <label class="text-xs text-zinc-500 uppercase font-bold tracking-wider mb-1">Nombre Común</label>
                        <input type="text" id="nombre_comun" name="nombre_comun" placeholder="Ej: Peuco" required onkeyup="actualizarNombreCientifico()" class="bg-zinc-950 border border-zinc-700 p-3 rounded-lg text-sm focus:border-emerald-500 outline-none w-full">
                    </div>
                    <div class="col-span-2 md:col-span-1 flex flex-col justify-end">
                        <label class="text-xs text-zinc-500 uppercase font-bold tracking-wider mb-1">Nombre Científico (Automático)</label>
                        <input type="text" id="nombre_cientifico" name="nombre_cientifico" placeholder="Se llena solo..." required class="bg-zinc-800 border border-zinc-700 p-3 rounded-lg text-sm focus:border-emerald-500 outline-none w-full text-zinc-300">
                    </div>
                </div>
                
                <!-- Columna 3: Detalles -->
                <div class="lg:col-span-1 space-y-2 grid grid-cols-2 gap-4">
                    <div class="col-span-1 flex flex-col justify-end">
                        <label class="text-xs text-zinc-500 uppercase font-bold tracking-wider mb-1">Cantidad</label>
                        <input type="number" name="numero_ejemplar" value="1" min="1" required class="bg-zinc-950 border border-zinc-700 p-3 rounded-lg text-sm focus:border-emerald-500 outline-none w-full">
                    </div>
                    <div class="col-span-1 flex flex-col justify-end">
                        <label class="text-xs text-zinc-500 uppercase font-bold tracking-wider mb-1">N° Acta</label>
                        <input type="text" name="numero_acta_movimiento" placeholder="Opcional" class="bg-zinc-950 border border-zinc-700 p-3 rounded-lg text-sm focus:border-emerald-500 outline-none w-full">
                    </div>
                </div>

                <!-- Fila 2 -->
                <div class="lg:col-span-1 flex flex-col justify-end">
                    <label class="text-xs text-zinc-500 uppercase font-bold tracking-wider mb-1">Categoría del Evento</label>
                    <input type="text" name="categoria_evento" placeholder="Ej: SAG Río Negro" class="bg-zinc-950 border border-zinc-700 p-3 rounded-lg text-sm focus:border-emerald-500 outline-none w-full">
                </div>
                
                <div class="lg:col-span-1 flex flex-col justify-end">
                    <label class="text-xs text-zinc-500 uppercase font-bold tracking-wider mb-1">Destino</label>
                    <input type="text" name="destino" placeholder="Ej: Rehabilitación" class="bg-zinc-950 border border-zinc-700 p-3 rounded-lg text-sm focus:border-emerald-500 outline-none w-full">
                </div>
                
                <div class="lg:col-span-2 flex flex-col justify-end">
                    <label class="text-xs text-zinc-500 uppercase font-bold tracking-wider mb-1">Observación</label>
                    <div class="flex gap-4">
                        <input type="text" name="observacion" placeholder="Detalles adicionales..." class="flex-1 bg-zinc-950 border border-zinc-700 p-3 rounded-lg text-sm focus:border-emerald-500 outline-none">
                        <button type="submit" class="bg-emerald-700 hover:bg-emerald-600 transition-colors font-bold px-8 rounded-lg shadow-lg">GUARDAR</button>
                    </div>
                </div>

            </div>
            
            <p class="text-xs text-zinc-500 mt-4 italic">* El sistema calculará el número de ficha y los saldos automáticamente al guardar.</p>
        </form>

        <div class="bg-zinc-900 p-6 rounded-xl border border-zinc-800 overflow-x-auto shadow-xl">
            <h2 class="text-xl text-zinc-400 mb-4 border-b border-zinc-800 pb-2">Últimos Registros</h2>
            <table class="w-full text-sm text-left">
                <thead class="text-zinc-500 uppercase border-b border-zinc-700 bg-zinc-950/50">
                    <tr>
                        <th class="py-3 px-2">Ficha</th>
                        <th class="py-3 px-2">Fecha</th>
                        <th class="py-3 px-2">Tipo</th>
                        <th class="py-3 px-2">Especie</th>
                        <th class="py-3 px-2 text-center">Cant.</th>
                        <th class="py-3 px-2 text-center">Saldo</th>
                        <th class="py-3 px-2">Obs</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-zinc-800">
                    {% for r in lista %}
                    <tr class="hover:bg-zinc-800/50 transition-colors">
                        <td class="py-3 px-2 font-mono text-emerald-400 font-bold">{{ r.numero_ficha or '-' }}</td>
                        <td class="py-3 px-2 text-zinc-400">{{ r.fecha[:10] if r.fecha else '-' }}</td>
                        <td class="py-3 px-2">
                            {% if r.tipo_evento == 'Ingreso' %}
                                <span class="bg-emerald-900 text-emerald-300 px-2 py-1 rounded text-xs">Ingreso</span>
                            {% else %}
                                <span class="bg-orange-900 text-orange-300 px-2 py-1 rounded text-xs">Egreso</span>
                            {% endif %}
                        </td>
                        <td class="py-3 px-2">
                            <div>{{ r.nombre_comun or '-' }}</div>
                            <div class="text-xs text-zinc-500 italic">{{ r.nombre_cientifico or '-' }}</div>
                        </td>
                        <td class="py-3 px-2 text-center font-bold text-zinc-300">{{ r.numero_ejemplar or '1' }}</td>
                        <td class="py-3 px-2 text-center">
                            <span class="bg-zinc-950 px-2 py-1 rounded border border-zinc-700 font-mono">{{ r.saldo_actual or '0' }}</span>
                        </td>
                        <td class="py-3 px-2 text-zinc-400 text-xs">{{ r.observacion or '-' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% if not lista %}
                <p class="text-center text-zinc-500 my-8 italic">No hay registros guardados aún.</p>
            {% endif %}
        </div>
    </div>

    <!-- DICCIONARIO PARA AUTOCOMPLETAR -->
    <script>
        const diccionarioEspecies = {
            "PEUCO": "Parabuteo unicinctus",
            "GOLONDRINA": "Tachycineta leucopyga",
            "PUDU": "Pudu puda",
            "CHOROY": "Enicognathus leptorhynchus",
            "LECHUZA": "Tyto alba",
            "CHILLA": "Lycalopex griseus",
            "CULPEO": "Lycalopex culpaeus",
            "PUMA": "Puma concolor",
            "CONDOR": "Vultur gryphus"
            // Puedes agregar más aquí abajo fácilmente!
        };

        function actualizarNombreCientifico() {
            const comun = document.getElementById("nombre_comun").value.toUpperCase();
            const inputCientifico = document.getElementById("nombre_cientifico");
            
            let encontrado = false;
            if (comun.length >= 3) {
                for(let clave in diccionarioEspecies) {
                    if(comun.includes(clave)) {
                        inputCientifico.value = diccionarioEspecies[clave];
                        encontrado = true;
                        break;
                    }
                }
            }
            if(!encontrado && comun.length < 3) {
                inputCientifico.value = "";
            }
        }
    </script>
    </body></html>
    """
    return render_template_string(html, lista=lista, error_msg=error_msg, exito_msg=exito_msg)

@app.route('/web/registrar', methods=['POST'])
def web_registrar():
    try:
        url, headers = get_supabase_headers()
        
        # Datos extraídos del formulario frontend
        nombre_comun = request.form.get('nombre_comun', '')
        nombre_cientifico = request.form.get('nombre_cientifico', '')
        tipo_evento = request.form.get('tipo_evento', 'Ingreso')
        numero_ejemplar_str = request.form.get('numero_ejemplar')
        
        try:
            qty = int(numero_ejemplar_str)
        except:
            qty = 1
            
        # Fechas y Autogeneración
        ahora = datetime.datetime.now()
        fecha_str = ahora.isoformat()
        anio_actual = ahora.year

        # 1. Calcular Saldo Actual (por especie/nombre científico)
        saldo_anterior = 0
        resp_saldo = requests.get(
            f"{url}/rest/v1/registro_evento?nombre_cientifico=eq.{requests.utils.quote(nombre_cientifico)}&select=saldo_actual&order=created_at.desc&limit=1", 
            headers=headers
        )
        if resp_saldo.status_code == 200 and resp_saldo.json():
            val = resp_saldo.json()[0].get('saldo_actual', 0)
            saldo_anterior = int(val) if val else 0
            
        if tipo_evento == 'Ingreso':
            saldo_actual = saldo_anterior + qty
        else:
            saldo_actual = max(0, saldo_anterior - qty) # Evitar saldos negativos
            
        # 2. Generar N° Ficha automático (Formato: F-YYYY-XXX)
        resp_fichas = requests.get(
            f"{url}/rest/v1/registro_evento?fecha=gte.{anio_actual}-01-01T00:00:00&select=id",
            headers=headers
        )
        count_anio = 0
        if resp_fichas.status_code == 200:
            count_anio = len(resp_fichas.json())
            
        numero_ficha = f"F-{anio_actual}-{(count_anio + 1):03d}"
        
        # Agrupar todos los datos para Supabase
        datos = {
            "fecha": fecha_str,
            "numero_ficha": numero_ficha,
            "numero_acta_movimiento": request.form.get('numero_acta_movimiento'),
            "nombre_comun": nombre_comun,
            "nombre_cientifico": nombre_cientifico,
            "numero_ejemplar": qty,
            "tipo_evento": tipo_evento,
            "categoria_evento": request.form.get('categoria_evento'),
            "saldo_anterior": saldo_anterior,
            "saldo_actual": saldo_actual,
            "destino": request.form.get('destino'),
            "observacion": request.form.get('observacion')
        }
        
        # Enviar petición POST a Supabase
        response = requests.post(f"{url}/rest/v1/registro_evento", json=datos, headers=headers)
        if response.status_code >= 400:
            raise Exception(f"Error guardando en Supabase: {response.text}")
            
        return redirect(url_for('index', exito=f"Ficha {numero_ficha} registrada ({tipo_evento}). Saldo actual de {nombre_comun}: {saldo_actual}"))
        
    except Exception as e:
        return redirect(url_for('index', error=str(e)))

application = app

if __name__ == '__main__':
    app.run(debug=True, port=5000)