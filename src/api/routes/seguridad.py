from flask import Blueprint, session, jsonify, request

from src.api.auth_service import verificar_acceso_a_pantalla
from src.database.repository import actualizar_desde_modal

seguridad_bp = Blueprint('seguridad_fauna', __name__)


@seguridad_bp.route('/api/fauna/seguridad/modificar/<string:id_registro>', methods=['POST'])
def verificar_y_modificar(id_registro):
    """Valida modificar_fichas antes de habilitar edición en el modal."""
    rol_usuario = session.get('rol')
    usuario_correo = session.get('usuario')
    tiene_permiso = verificar_acceso_a_pantalla(rol_usuario, "modificar_fichas")

    if not tiene_permiso:
        return jsonify({
            "autorizado": False,
            "mensaje": f"Acceso denegado: El usuario '{usuario_correo}' no tiene permisos para modificar registros."
        }), 403

    return jsonify({"autorizado": True, "id_paciente": id_registro}), 200


@seguridad_bp.route('/api/fauna/seguridad/actualizar/<string:id_registro>', methods=['POST'])
def actualizar_en_modal(id_registro):
    """Guarda en Supabase vía repository.actualizar_desde_modal."""
    rol_usuario = session.get('rol')
    if not verificar_acceso_a_pantalla(rol_usuario, "modificar_fichas"):
        return jsonify({"error": "Sin permisos para modificar registros."}), 403

    datos = request.get_json(silent=True) or {}
    try:
        payload, status = actualizar_desde_modal(id_registro, datos)
        return jsonify(payload), status
    except Exception as e:
        return jsonify({"error": f"No se pudo actualizar: {str(e)}"}), 500


