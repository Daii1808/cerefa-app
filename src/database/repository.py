import os
import requests
import datetime

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

def verificar_medico(correo, password):
    url, headers = get_supabase_headers()
    resp = requests.get(f"{url}/rest/v1/usuarios?correo=eq.{requests.utils.quote(correo)}&password=eq.{requests.utils.quote(password)}&select=id", headers=headers)
    if resp.status_code == 200 and len(resp.json()) > 0:
        return True
    return False

def obtener_ultimos_registros(limite=50):
    url, headers = get_supabase_headers()
    resp = requests.get(f"{url}/rest/v1/registro_evento?select=*&order=fecha_creacion.desc&limit={limite}", headers=headers)
    if resp.status_code == 200:
        return resp.json()
    raise Exception(f"Error de Supabase: {resp.text}")

def obtener_inventario_actual():
    url, headers = get_supabase_headers()
    resp = requests.get(f"{url}/rest/v1/registro_evento?select=nombre_comun,saldo_actual&order=fecha_creacion.desc", headers=headers)
    inventario = {}
    if resp.status_code == 200:
        for r in resp.json():
            nc = r.get('nombre_comun')
            if nc and nc not in inventario:
                inventario[nc] = r.get('saldo_actual', 0)
    return {k: v for k, v in inventario.items() if v > 0}

def obtener_fichas_activas():
    url, headers = get_supabase_headers()
    # Obtenemos los registros ordenados cronológicamente para reconstruir el historial por ficha
    resp = requests.get(f"{url}/rest/v1/registro_evento?select=numero_ficha,nombre_comun,tipo_evento,numero_ejemplar,observacion,destino&order=fecha_creacion.asc", headers=headers)
    fichas_activas = {}
    
    if resp.status_code == 200:
        registros = resp.json()
        fichas_estado = {}
        
        for r in registros:
            ficha = r.get('numero_ficha')
            if not ficha or ficha == 'None': continue
            
            especie = r.get('nombre_comun')
            tipo = r.get('tipo_evento')
            try:
                qty = int(r.get('numero_ejemplar') or 1)
            except:
                qty = 1
                
            obs = r.get('observacion') or 'Sin observaciones'
            destino = r.get('destino') or 'En centro'
            
            if ficha not in fichas_estado:
                fichas_estado[ficha] = {'saldo': 0, 'especie': especie, 'obs': obs, 'destino': destino}
            
            if tipo == 'Ingreso':
                fichas_estado[ficha]['saldo'] += qty
            elif tipo == 'Egreso':
                fichas_estado[ficha]['saldo'] -= qty
                
            # Actualizamos la última observación y estado
            if obs != 'Sin observaciones' and obs != '':
                fichas_estado[ficha]['obs'] = obs
            if destino != 'En centro' and destino != '':
                fichas_estado[ficha]['destino'] = destino
                
        # Agrupamos las fichas con saldo positivo (Activas en el centro) por especie
        for ficha, data in fichas_estado.items():
            if data['saldo'] > 0:
                especie = data['especie']
                if not especie: continue
                if especie not in fichas_activas:
                    fichas_activas[especie] = []
                fichas_activas[especie].append({
                    'ficha': ficha,
                    'estado': data['destino'],
                    'observacion': data['obs']
                })
                
    return fichas_activas

def registrar_evento(datos_form, usuario_email):
    url, headers = get_supabase_headers()
    
    tipo_evento = datos_form.get('tipo_evento', 'Ingreso')
    try:
        qty = int(datos_form.get('numero_ejemplar'))
    except:
        qty = 1
        
    ahora = datetime.datetime.now()
    fecha_str = ahora.isoformat()
    anio_actual = ahora.year

    nombre_comun = ""
    nombre_cientifico = ""
    numero_ficha = ""

    if tipo_evento == 'Egreso':
        ficha_existente = datos_form.get('numero_ficha_existente', '').strip()
        if not ficha_existente:
            raise Exception("Debes indicar la Ficha para un egreso.")
        
        numero_ficha = ficha_existente
        resp_ficha = requests.get(f"{url}/rest/v1/registro_evento?numero_ficha=eq.{requests.utils.quote(ficha_existente)}&select=nombre_comun,nombre_cientifico&limit=1", headers=headers)
        if resp_ficha.status_code == 200 and resp_ficha.json():
            nombre_comun = resp_ficha.json()[0].get('nombre_comun', '')
            nombre_cientifico = resp_ficha.json()[0].get('nombre_cientifico', '')
        else:
            raise Exception("Ficha no encontrada.")
    else:
        nombre_comun = datos_form.get('nombre_comun', '').strip()
        nombre_cientifico = datos_form.get('nombre_cientifico', '').strip()
        resp_fichas = requests.get(f"{url}/rest/v1/registro_evento?fecha_creacion=gte.{anio_actual}-01-01T00:00:00&tipo_evento=eq.Ingreso&select=id", headers=headers)
        count_anio = len(resp_fichas.json()) if resp_fichas.status_code == 200 else 0
        numero_ficha = f"F-{(count_anio + 1):03d}-{anio_actual}"

    saldo_anterior = 0
    resp_saldo = requests.get(
        f"{url}/rest/v1/registro_evento?nombre_cientifico=eq.{requests.utils.quote(nombre_cientifico)}&select=saldo_actual&order=fecha_creacion.desc&limit=1", 
        headers=headers
    )
    if resp_saldo.status_code == 200 and resp_saldo.json():
        val = resp_saldo.json()[0].get('saldo_actual', 0)
        saldo_anterior = int(val) if val else 0
        
    saldo_actual = saldo_anterior + qty if tipo_evento == 'Ingreso' else max(0, saldo_anterior - qty)
        
    datos = {
        "fecha": fecha_str,
        "numero_ficha": numero_ficha,
        "numero_acta_movimiento": datos_form.get('numero_acta_movimiento'),
        "nombre_comun": nombre_comun,
        "nombre_cientifico": nombre_cientifico,
        "numero_ejemplar": qty,
        "tipo_evento": tipo_evento,
        "categoria_evento": datos_form.get('categoria_evento'),
        "saldo_anterior": saldo_anterior,
        "saldo_actual": saldo_actual,
        "destino": datos_form.get('destino'),
        "observacion": datos_form.get('observacion'),
        "doctor_email": usuario_email
    }
    
    resp_post = requests.post(f"{url}/rest/v1/registro_evento", json=datos, headers=headers)
    if resp_post.status_code >= 400:
        raise Exception(resp_post.text)
        
    return numero_ficha