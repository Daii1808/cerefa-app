from flask import Blueprint, jsonify, request
from src.database.models import Paciente
from src.core.fauna_service import FaunaService

fauna_bp = Blueprint('fauna', __name__)

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