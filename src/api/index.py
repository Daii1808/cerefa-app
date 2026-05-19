import sys
import os

# Mantiene tu estructura intacta, conectando con config/app.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from flask import Flask, render_template_string, request, redirect, url_for
from config.app import app, supabase

@app.route('/')
def index():
    error_msg = request.args.get('error')
    exito_msg = request.args.get('exito')
    
    try:
        response = supabase.table('registro_evento').select("*").execute()
        lista = response.data
    except Exception as e:
        lista = []
        if not error_msg:
            error_msg = f"Error al cargar BD: {str(e)}"

    html = """
    <!DOCTYPE html>
    <html lang="es"><head><script src="https://cdn.tailwindcss.com"></script></head>
    <body class="bg-zinc-950 text-white p-8">
    <div class="max-w-6xl mx-auto">
        <h1 class="text-3xl font-bold mb-6">🐾 Panel de Control CEREFA</h1>
        
        {% if error_msg %}
        <div class="bg-rose-900 p-4 mb-4 rounded text-xs font-mono border border-rose-700">❌ ERROR: {{ error_msg }}</div>
        {% endif %}
        
        {% if exito_msg %}
        <div class="bg-emerald-900 p-4 mb-4 rounded text-xs font-mono border border-emerald-700">✅ ÉXITO: {{ exito_msg }}</div>
        {% endif %}

        <form action="/web/registrar" method="POST" class="grid grid-cols-2 lg:grid-cols-6 gap-4 bg-zinc-900 p-6 rounded-xl border border-zinc-800 mb-8">
            <input type="text" name="numero_ficha" placeholder="N° Ficha" required class="bg-zinc-950 border border-zinc-700 p-2 rounded text-sm focus:border-emerald-500 outline-none">
            <input type="text" name="numero_acta_movimiento" placeholder="N° Acta" class="bg-zinc-950 border border-zinc-700 p-2 rounded text-sm focus:border-emerald-500 outline-none">
            <input type="text" name="nombre_comun" placeholder="Especie" required class="bg-zinc-950 border border-zinc-700 p-2 rounded text-sm focus:border-emerald-500 outline-none">
            <input type="text" name="categoria_evento" placeholder="Categoría" class="bg-zinc-950 border border-zinc-700 p-2 rounded text-sm focus:border-emerald-500 outline-none">
            <input type="text" name="destino" placeholder="Destino" class="bg-zinc-950 border border-zinc-700 p-2 rounded text-sm focus:border-emerald-500 outline-none">
            <button type="submit" class="bg-emerald-700 hover:bg-emerald-600 transition-colors font-bold p-2 rounded text-sm cursor-pointer">GUARDAR</button>
            <input type="text" name="observacion" placeholder="Observación" class="col-span-2 lg:col-span-6 bg-zinc-950 border border-zinc-700 p-2 rounded text-sm focus:border-emerald-500 outline-none">
        </form>

        <div class="bg-zinc-900 p-6 rounded-xl border border-zinc-800 overflow-x-auto shadow-xl">
            <table class="w-full text-sm text-left">
                <thead class="text-zinc-500 uppercase border-b border-zinc-700 bg-zinc-950/50">
                    <tr><th class="py-3 px-2">Ficha</th><th class="py-3 px-2">Acta</th><th class="py-3 px-2">Especie</th><th class="py-3 px-2">Cat</th><th class="py-3 px-2">Destino</th><th class="py-3 px-2">Obs</th></tr>
                </thead>
                <tbody class="divide-y divide-zinc-800">
                    {% for r in lista %}
                    <tr class="hover:bg-zinc-800/50 transition-colors">
                        <td class="py-3 px-2 font-mono text-emerald-400">{{ r.numero_ficha }}</td>
                        <td class="py-3 px-2">{{ r.numero_acta_movimiento or '-' }}</td>
                        <td class="py-3 px-2">{{ r.nombre_comun or '-' }}</td>
                        <td class="py-3 px-2">{{ r.categoria_evento or '-' }}</td>
                        <td class="py-3 px-2">{{ r.destino or '-' }}</td>
                        <td class="py-3 px-2 text-zinc-400">{{ r.observacion or '-' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% if not lista %}
                <p class="text-center text-zinc-500 my-4 italic">No hay registros guardados aún.</p>
            {% endif %}
        </div>
    </div></body></html>
    """
    return render_template_string(html, lista=lista, error_msg=error_msg, exito_msg=exito_msg)

@app.route('/web/registrar', methods=['POST'])
def web_registrar():
    try:
        # Extraemos los datos del formulario
        datos = {
            "numero_ficha": request.form.get('numero_ficha'),
            "numero_acta_movimiento": request.form.get('numero_acta_movimiento'),
            "nombre_comun": request.form.get('nombre_comun'),
            "categoria_evento": request.form.get('categoria_evento'),
            "destino": request.form.get('destino'),
            "observacion": request.form.get('observacion')
        }
        
        # Intentamos insertar en Supabase
        resultado = supabase.table('registro_evento').insert(datos).execute()
        
        # Si funciona, recargamos la página con mensaje de éxito
        return redirect(url_for('index', exito="Registro guardado correctamente"))
        
    except Exception as e:
        # Si falla, te mostramos el error exacto en pantalla
        return redirect(url_for('index', error=str(e)))

# Requerido por Vercel
application = app