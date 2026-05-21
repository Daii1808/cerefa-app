from datetime import datetime

from flask import Blueprint, jsonify, request, session
from src.database.models import Paciente
from src.core.fauna_service import FaunaService
from src.api.auth_service import verificar_acceso_a_pantalla

fauna_bp = Blueprint('fauna', __name__)


def _asignar_campo(paciente, nombres_posibles, valor):
    """Asigna valor al primer atributo que exista en el modelo Paciente."""
    for nombre in nombres_posibles:
        if hasattr(paciente, nombre):
            setattr(paciente, nombre, valor)
            return True
    return False


def _parsear_fecha(valor):
    """Acepta 'YYYY-MM-DD' desde input type=date del modal."""
    if not valor:
        return None
    texto = str(valor).strip()[:10]
    return datetime.strptime(texto, "%Y-%m-%d").date()

@fauna_bp.route('/api/fauna/historial', methods=['GET'])
def obtener_historial():
    registros = Paciente.query.order_by(Paciente.fecha_registro.desc()).all()
    return jsonify([r.to_dict() for r in registros]), 200

@fauna_bp.route('/api/fauna/ingreso', methods=['POST'])
def registrar_ingreso():
    datos = request.get_json() or {}
    resultado, estatus = FaunaService.registrar_paciente_logica(datos)
   
    if "error" in resultado:
        return jsonify(resultado), estatus
    return jsonify(resultado), estatus

# ==========================================
# API para edición en modal (index.html)
# Permiso requerido al guardar: modificar_fichas (auth_service.py)
# ==========================================

@fauna_bp.route('/api/fauna/obtener/<int:id_paciente>', methods=['GET'])
def obtener_paciente_editar(id_paciente):
    """
    Devuelve JSON del paciente para el modal de detalle/edición en index.html.
    Cualquier usuario con acceso al panel puede consultar (ver_fichas en listado).
    """
    paciente = Paciente.query.get(id_paciente)
   
    if not paciente:
        return jsonify({"error": "El registro del paciente no existe."}), 404
       
    return jsonify(paciente.to_dict()), 200


@fauna_bp.route('/api/fauna/actualizar/<int:id_paciente>', methods=['POST'])
def actualizar_paciente(id_paciente):
    """
    Persiste cambios desde el modal. Revalida modificar_fichas en servidor
    (no basta con la verificación previa en seguridad.py).
    Solo actualiza campos presentes en el JSON para no borrar datos con None.
    """
    rol_usuario = session.get('rol')
    if not verificar_acceso_a_pantalla(rol_usuario, "modificar_fichas"):
        return jsonify({"error": "Sin permisos para modificar registros."}), 403

    paciente = Paciente.query.get(id_paciente)
    if not paciente:
        return jsonify({"error": "Paciente no encontrado"}), 404
       
    datos = request.get_json() or {}
    campos_actualizados = []

    try:
        if 'destino' in datos:
            _asignar_campo(paciente, ('destino',), datos['destino'])
            campos_actualizados.append('destino')

        if 'observacion_medica' in datos or 'observacion' in datos:
            obs = datos.get('observacion_medica', datos.get('observacion'))
            if _asignar_campo(paciente, ('observacion_medica', 'observacion'), obs):
                campos_actualizados.append('observacion')

        if 'categoria' in datos:
            _asignar_campo(paciente, ('categoria', 'categoria_evento'), datos['categoria'])
            campos_actualizados.append('categoria')

        if 'numero_acta_movimiento' in datos:
            _asignar_campo(paciente, ('numero_acta_movimiento',), datos['numero_acta_movimiento'])
            campos_actualizados.append('numero_acta_movimiento')

        if 'fecha' in datos and datos['fecha']:
            fecha_parsed = _parsear_fecha(datos['fecha'])
            asignado = False
            for nombre in ('fecha_registro', 'fecha'):
                if hasattr(paciente, nombre):
                    # DateTime en BD: usar datetime; Date: usar date
                    valor = datetime.combine(fecha_parsed, datetime.min.time())
                    setattr(paciente, nombre, valor)
                    asignado = True
                    break
            if asignado:
                campos_actualizados.append('fecha')

        if not campos_actualizados:
            return jsonify({"error": "No se recibieron campos para actualizar."}), 400

        from src.config.app import db
        db.session.commit()

        return jsonify({"success": True, "mensaje": "Registro actualizado con éxito"}), 200
    except ValueError:
        db.session.rollback()
        return jsonify({"error": "Formato de fecha inválido. Use AAAA-MM-DD."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"No se pudo actualizar: {str(e)}"}), 500