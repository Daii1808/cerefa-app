import os
from flask import Flask
from dotenv import load_dotenv
load_dotenv()
# Configuramos Flask para que busque el HTML en src/ui/templates
directorio_templates = os.path.abspath(os.path.join(os.path.dirname(__file__), '../ui/templates'))
app = Flask(__name__, template_folder=directorio_templates)
application = app