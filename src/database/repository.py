import os
import requests
import datetime
import unicodedata
import re

def normalizar_compara_py(text):
    if not text:
        return ""
    text_normalized = unicodedata.normalize("NFD", text)
    text_without_accents = "".join(c for c in text_normalized if unicodedata.category(c) != "Mn").lower()
    text_clean = re.sub(r"[^a-z]", "", text_without_accents)
    return text_clean

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

def obtener_usuario_por_correo(correo):
    try:
        url, headers = get_supabase_headers()
        
        url_consulta = f"{url}/rest/v1/usuarios?correo=eq.{requests.utils.quote(correo)}&select=*"
        
        resp = requests.get(url_consulta, headers=headers)
        
        if resp.status_code == 200:
            datos = resp.json()
            if len(datos) > 0:
                return datos[0]
                
        return None
    except Exception as e:
        print(f"Error al obtener usuario por correo: {str(e)}")
        return None

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
                
            if obs != 'Sin observaciones' and obs != '':
                fichas_estado[ficha]['obs'] = obs
            if destino != 'En centro' and destino != '':
                fichas_estado[ficha]['destino'] = destino
                
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
        raw_comun = datos_form.get('nombre_comun', '').strip()
        nombre_comun = " ".join(raw_comun.split()).upper()

        raw_cientifico = datos_form.get('nombre_cientifico', '').strip()
        partes_cientifico = raw_cientifico.split()
        if partes_cientifico:
            partes_cientifico[0] = partes_cientifico[0].capitalize()
            for idx in range(1, len(partes_cientifico)):
                partes_cientifico[idx] = partes_cientifico[idx].lower()
            nombre_cientifico = " ".join(partes_cientifico)
        else:
            nombre_cientifico = ""

        if not nombre_comun or not nombre_cientifico:
            raise Exception("Debes ingresar el Nombre Común y Científico para registrar un Ingreso.")

        resp_search = requests.get(f"{url}/rest/v1/registro_evento?select=nombre_comun,nombre_cientifico", headers=headers)
        if resp_search.status_code == 200:
            especies_existentes = {}
            for reg in resp_search.json():
                c_name = reg.get('nombre_comun')
                s_name = reg.get('nombre_cientifico')
                if c_name and s_name:
                    especies_existentes[normalizar_compara_py(c_name)] = {
                        "comun": c_name,
                        "cientifico": s_name
                    }
            
            nombre_comun_limpio = normalizar_compara_py(nombre_comun)
            cientifico_limpio = normalizar_compara_py(nombre_cientifico)

            if nombre_comun_limpio in especies_existentes:
                dup = especies_existentes[nombre_comun_limpio]
                if normalizar_compara_py(dup["cientifico"]) != cientifico_limpio:
                    raise Exception(f"La especie '{dup['comun']}' ya está registrada con el nombre científico '{dup['cientifico']}'. No puedes registrarla como '{nombre_cientifico}'.")

            for dup in especies_existentes.values():
                if normalizar_compara_py(dup["cientifico"]) == cientifico_limpio:
                    if normalizar_compara_py(dup["comun"]) != nombre_comun_limpio:
                        raise Exception(f"El nombre científico '{nombre_cientifico}' ya está registrado para la especie '{dup['comun']}'. No puedes usarlo para '{nombre_comun}'.")

        resp_fichas = requests.get(f"{url}/rest/v1/registro_evento?fecha_creacion=gte.{anio_actual}-01-01T00:00:00&tipo_evento=eq.Ingreso&select=id", headers=headers)
        count_anio = len(resp_fichas.json()) if resp_fichas.status_code == 200 else 0
        numero_ficha = f"{anio_actual}-{(count_anio + 1):03d}"

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


def actualizar_desde_modal(id_registro, datos):
    """
    Actualiza campos editables del modal en Supabase (tabla registro_evento).
    id_registro: id del registro en lista (o numero_ficha como respaldo).
    Retorna (dict, codigo_http).
    """
    url, headers = get_supabase_headers()
    patch = {}

    if "destino" in datos:
        patch["destino"] = datos["destino"]

    if "observacion_medica" in datos or "observacion" in datos:
        patch["observacion"] = datos.get("observacion_medica", datos.get("observacion"))

    if "numero_acta_movimiento" in datos:
        patch["numero_acta_movimiento"] = datos["numero_acta_movimiento"]

    if datos.get("fecha"):
        fecha = str(datos["fecha"]).strip()[:10]
        patch["fecha"] = fecha if "T" in fecha else f"{fecha}T12:00:00"

    if not patch:
        return {"error": "No se recibieron campos para actualizar."}, 400

    id_str = str(id_registro).strip()
    filtros = [
        f"id=eq.{requests.utils.quote(id_str)}",
        f"numero_ficha=eq.{requests.utils.quote(id_str)}",
    ]

    ultimo_error = "Registro no encontrado"
    for filtro in filtros:
        resp = requests.patch(
            f"{url}/rest/v1/registro_evento?{filtro}",
            json=patch,
            headers=headers,
        )
        if resp.status_code in (200, 204):
            return {"success": True, "mensaje": "Registro actualizado con éxito"}, 200
        ultimo_error = resp.text or ultimo_error

    return {"error": f"No se pudo actualizar: {ultimo_error}"}, 400

def registrar_usuario(correo, password, rol='practicante'):
    url, headers = get_supabase_headers()
    
    resp = requests.get(f"{url}/rest/v1/usuarios?correo=eq.{requests.utils.quote(correo)}", headers=headers)
    if resp.status_code == 200 and len(resp.json()) > 0:
        return False, "El correo ya está registrado."
        
    datos = {
        "correo": correo,
        "password": password,
        "rol": rol
    }
    
    resp_post = requests.post(f"{url}/rest/v1/usuarios", json=datos, headers=headers)
    if resp_post.status_code >= 400:
        return False, f"Error al registrar: {resp_post.text}"
        
    return True, "Usuario registrado exitosamente."