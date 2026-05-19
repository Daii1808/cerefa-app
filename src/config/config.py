import os

class Config:
    # TRUCO MAESTRO: Si está en Vercel, usa la carpeta temporal /tmp para que no explote.
    # Si está en tu computador, sigue usando el archivo normal en la raíz.
    if os.environ.get('VERCEL') == '1':
        SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/cerefa.db'
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///cerefa.db')
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cerefa_secret_key_2026')