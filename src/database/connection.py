from flask_sqlalchemy import SQLAlchemy

# Esta es la famosa variable 'db' que todo el resto de tu proyecto 
# (el index.py y el pacientes.py) está buscando para conectarse.
db = SQLAlchemy()
