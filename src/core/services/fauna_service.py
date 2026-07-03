from src.database.models import db, Paciente
from datetime import datetime

class FaunaService:
    @staticmethod
    def calcular_siguiente_correlativo(anio):
        ultimo = Paciente.query.filter_by(anio_registro=anio)\
                               .order_by(Paciente.numero_registro.desc()).first()
        return (ultimo.numero_registro + 1) if ultimo else 1

    @staticmethod
    def registrar_paciente_logica(datos):
        if not datos.get('nombre_comun') or not datos.get('tipo_evento'):
            return {"error": "Campos obligatorios faltantes"}, 400

        anio_actual = datetime.now().year
        siguiente_num = FaunaService.calcular_siguiente_correlativo(anio_actual)
        id_inteligente = f"{anio_actual}-{str(siguiente_num).zfill(3)}"

        ultimo_registro_global = Paciente.query.order_by(Paciente.fecha_registro.desc()).first()
        saldo_ant = ultimo_registro_global.saldo_actual if ultimo_registro_global else 0
        
        modificador = 1 if datos.get('tipo_evento').lower() == 'ingreso' else -1
        saldo_act = saldo_ant + modificador

        nuevo_paciente = Paciente(
            id=id_inteligente,
            numero_registro=siguiente_num,
            anio_registro=anio_actual,
            nombre_comun=datos.get('nombre_comun'),
            nombre_cientifico=datos.get('nombre_cientifico', 'No especificado'),
            num_acta_movimiento=datos.get('num_acta', ''),
            tipo_evento=datos.get('tipo_evento'),
            categoria_evento=datos.get('categoria_evento', 'Particular'),
            saldo_anterior=saldo_ant,
            saldo_actual=saldo_act,
            destino=datos.get('destino', 'Rehabilitación'),
            observacion=datos.get('observacion', '')
        )

        db.session.add(nuevo_paciente)
        db.session.commit()
        return {"mensaje": "¡Sincronizado con éxito!", "id": id_inteligente}, 201