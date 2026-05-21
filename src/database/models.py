from datetime import datetime

from src.database.connection import db  # única instancia SQLAlchemy (ver connection.py)

class Paciente(db.Model):
    __tablename__ = 'pacientes'

    # ID inteligente único: '2026-001'
    id = db.Column(db.String(20), primary_key=True)
    numero_registro = db.Column(db.Integer, nullable=False)
    anio_registro = db.Column(db.Integer, nullable=False)
    
    # Datos extraídos de tus planillas de Excel del CEREFA
    nombre_comun = db.Column(db.String(100), nullable=False)
    nombre_cientifico = db.Column(db.String(100))
    num_acta_movimiento = db.Column(db.String(50))
    num_ejemplar = db.Column(db.Integer, default=1)
    
    tipo_evento = db.Column(db.String(20), nullable=False) # Ingreso o Egreso
    categoria_evento = db.Column(db.String(100))          # Particular, SAG, etc.
    
    # Control automatizado de saldos (evita errores manuales)
    saldo_anterior = db.Column(db.Integer, default=0)
    saldo_actual = db.Column(db.Integer, default=0)
    
    destino = db.Column(db.String(100)) 
    observacion = db.Column(db.Text)
    fecha_registro = db.Column(db.Date, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "fecha": self.fecha_registro.strftime("%Y-%m-%d") if self.fecha_registro else None,
            "nombre_comun": self.nombre_comun,
            "nombre_cientifico": self.nombre_cientifico,
            "num_acta": self.num_acta_movimiento,
            "tipo_evento": self.tipo_evento,
            "saldo_anterior": self.saldo_anterior,
            "saldo_actual": self.saldo_actual,
            "destino": self.destino,
            "observacion": self.observacion
        }