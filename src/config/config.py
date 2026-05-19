import os

class Config:
    # EL ENCHUFE REAL: Busca la variable del servidor en la nube.
    # Si estás en local haciendo pruebas, usará un archivo de respaldo temporal para que no crashee.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///cerefa_local_dev.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cerefa_produccion_segura_2026')