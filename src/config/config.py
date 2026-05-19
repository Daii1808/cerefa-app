import os

class Config:
    # Usa SQLite local por defecto en una base de datos llamada cerefa.db
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///cerefa.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cerefa_secret_key_2026')