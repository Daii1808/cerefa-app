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

def obtener_usuario_por_correo(correo):
    try:
        # Reutilizamos la misma configuración de tu compañero
        url, headers = get_supabase_headers()
        
        # Hacemos la consulta a la tabla 'usuarios' filtrando por el correo
        # Pedimos 'select=*' para traer todos los datos (incluyendo el rol)
        url_consulta = f"{url}/rest/v1/usuarios?correo=eq.{requests.utils.quote(correo)}&select=*"
        
        resp = requests.get(url_consulta, headers=headers)
        
        if resp.status_code == 200:
            datos = resp.json()
            if len(datos) > 0:
                return datos[0]  # Retorna el diccionario con todos los datos del usuario
                
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