from datetime import datetime
from database.connection import db  # Asegúrate de que esta ruta a tu "db" sea la correcta

class CatalogoFauna(db.Model):
    __tablename__ = 'catalogo_fauna'
    id = db.Column(db.Integer, primary_key=True)
    nombre_comun = db.Column(db.String(100), nullable=False, unique=True)
    nombre_cientifico = db.Column(db.String(100), nullable=True)


class RegistroEvento(db.Model):
    __tablename__ = 'registro_eventos'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow) # FECHA
    numero_ficha = db.Column(db.String(50), nullable=False) # N° ficha
    especie_id = db.Column(db.Integer, db.ForeignKey('catalogo_fauna.id'), nullable=False)
    
    # Campos del Excel del CEREFA
    numero_acta_movimiento = db.Column(db.String(50), nullable=True) # N° Acta de movimiento
    numero_ejemplar = db.Column(db.Integer, default=1) # N° de ejemplar
    tipo_evento = db.Column(db.String(50)) # Tipo de evento (Ingreso, Egreso, Reingreso, etc.)
    categoria_evento = db.Column(db.String(100), nullable=True) # Categoría del evento
    destino = db.Column(db.String(100), nullable=True) # Destino
    observacion = db.Column(db.Text, nullable=True) # Observación

    # CONTROL AUTOMÁTICO DE STOCK
    saldo_anterior = db.Column(db.Integer, nullable=False) # Saldo anterior
    saldo_actual = db.Column(db.Integer, nullable=False) # Saldo actual

    # Relación
    especie = db.relationship('CatalogoFauna', backref='eventos')

    @classmethod
    def registrar_con_saldo(cls, numero_ficha, nombre_comun, tipo_evento, numero_ejemplar=1, **kwargs):
        """
        MÉTODO DE OPTIMIZACIÓN: Calcula los saldos automáticamente mirando el historial 
        en la base de datos antes de guardar la nueva fila.
        """
        # 1. Validar que la especie exista en el catálogo
        especie = CatalogoFauna.query.filter_by(nombre_comun=nombre_comun.upper().strip()).first()
        if not especie:
            raise ValueError(f"La especie '{nombre_comun}' no existe en el catálogo oficial.")

        # 2. Buscar el último evento registrado de esa especie para sacar el saldo anterior
        ultimo = cls.query.filter_by(especie_id=especie.id).order_by(cls.fecha.desc()).first()
        saldo_anterior = ultimo.saldo_actual if ultimo else 0

        # 3. Calcular el saldo actual dinámicamente según el tipo de evento
        evento_limpio = tipo_evento.lower().strip()
        if evento_limpio in ['ingreso', 'reingreso', 'nacimiento']:
            saldo_actual = saldo_anterior + int(numero_ejemplar)
        elif evento_limpio in ['egreso', 'liberación', 'fallecido', 'eutanasia', 'traslado']:
            saldo_actual = max(0, saldo_anterior - int(numero_ejemplar))
        else:
            saldo_actual = saldo_anterior  # Si es solo una observación médica, el saldo no muta

        # 4. Crear la instancia del nuevo registro
        nuevo_registro = cls(
            numero_ficha=numero_ficha,
            especie_id=especie.id,
            tipo_evento=tipo_evento,
            numero_ejemplar=numero_ejemplar,
            saldo_anterior=saldo_anterior,
            saldo_actual=saldo_actual,
            numero_acta_movimiento=kwargs.get('numero_acta_movimiento'),
            categoria_evento=kwargs.get('categoria_evento'),
            destino=kwargs.get('destino'),
            observacion=kwargs.get('observacion')
        )

        db.session.add(nuevo_registro)
        db.session.commit()
        return nuevo_registro

    @classmethod
    def obtener_datos_dashboard(cls):
        """Saca todos los datos de la base de datos para que el index.py no tenga que hacerlo."""
        try:
            lista_eventos = cls.query.order_by(cls.fecha.desc()).all()
            especies = CatalogoFauna.query.order_by(CatalogoFauna.nombre_comun).all()
            total = cls.query.count()
            ultimo = cls.query.order_by(cls.id.desc()).first()
            return lista_eventos, especies, total, ultimo
        except Exception as e:
            print(f"Error de BD: {e}")
            return [], [], 0, None
