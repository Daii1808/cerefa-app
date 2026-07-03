


import os
import sys
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

ruta_config = os.path.dirname(os.path.abspath(__file__))
carpeta_src = os.path.abspath(os.path.join(ruta_config, '..'))

if carpeta_src not in sys.path:
    sys.path.insert(0, carpeta_src)

directorio_templates = os.path.abspath(os.path.join(carpeta_src, 'ui/templates'))

app = Flask(__name__, template_folder=directorio_templates)
application = app

app.secret_key = 'llave_secreta_para_los_permisos_de_fauna'

from api.routes.seguridad import seguridad_bp
app.register_blueprint(seguridad_bp)