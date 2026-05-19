import os

class Config:
    # SISTEMA REAL: Lee la base de datos externa desde las variables de entorno de Vercel.
    # Si estás probando en local y no hay variable, usará una base de datos de respaldo.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://usuario:password@servidor_real:5432/cerefa')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cerefa_produccion_segura_2026')