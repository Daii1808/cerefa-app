#import os
#from flask import Flask
#from dotenv import load_dotenv
#load_dotenv()
# Configuramos Flask para que busque el HTML en src/ui/templates
#directorio_templates = os.path.abspath(os.path.join(os.path.dirname(__file__), '../ui/templates'))
#app = Flask(__name__, template_folder=directorio_templates)
#application = app

#app.secret_key = 'llave_secreta_para_los_permisos_de_fauna'

#from src.api.routes.seguridad import seguridad_bp
#app.register_blueprint(seguridad_bp)

import os
import sys
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

# === LA SOLUCIÓN DEFINITIVA PARA TU ESTRUCTURA ===
# Como app.py está en 'src/config', subimos dos niveles para llegar a 'src'
ruta_config = os.path.dirname(os.path.abspath(__file__)) # c:\...\src\config
carpeta_src = os.path.abspath(os.path.join(ruta_config, '..')) # Sube a 'src'

# Le decimos a Python que 'src' es nuestra raíz de búsqueda
if carpeta_src not in sys.path:
    sys.path.insert(0, carpeta_src)

# Configuramos Flask (buscando los templates subiendo a 'src' y luego a 'ui/templates')
directorio_templates = os.path.abspath(os.path.join(carpeta_src, 'ui/templates'))

app = Flask(__name__, template_folder=directorio_templates)
application = app

app.secret_key = 'llave_secreta_para_los_permisos_de_fauna'

# Como Python ya está mirando dentro de 'src', encuentra 'api' de inmediato
from api.routes.seguridad import seguridad_bp
app.register_blueprint(seguridad_bp)