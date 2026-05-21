import sys
import os
import datetime

proyecto_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if proyecto_raiz not in sys.path:
    sys.path.insert(0, proyecto_raiz)

from flask import render_template, request, redirect, url_for, session
from src.config.app import app
from src.database import repository

# Configuración de Sesión y Seguridad
app.secret_key = 'cerefa_super_secret_key_2026'
app.permanent_session_lifetime = datetime.timedelta(minutes=10)

@app.before_request
def verificar_login():
    rutas_publicas = ['login', 'static']
    if request.endpoint not in rutas_publicas and 'usuario' not in session:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        correo = request.form.get('correo', '').strip().lower()
        password = request.form.get('password', '').strip()
        
        try:
            if repository.verificar_medico(correo, password):
                session.permanent = True
                session['usuario'] = correo
                
                datos_usuario = repository.obtener_usuario_por_correo(correo) 
                

                if datos_usuario and 'rol' in datos_usuario:
                    session['rol'] = datos_usuario['rol']
                else:
                    # Por si acaso no encuentra el rol, le dejas uno por defecto o manejas el error
                    session['rol'] = 'practicante' 
                # =======================

                return redirect(url_for('index'))
            else:
                error = "Correo o contraseña incorrectos."
        except Exception as e:
            error = f"Error de Supabase: {str(e)}"
            
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    error_msg = request.args.get('error')
    exito_msg = request.args.get('exito')
    try:
        lista = repository.obtener_ultimos_registros(50)
    except Exception as e:
        lista = []
        error_msg = str(e)
    return render_template('index.html', lista=lista, error_msg=error_msg, exito_msg=exito_msg, usuario=session.get('usuario'))

@app.route('/pacientes')
def pacientes():
    try:
        inventario = repository.obtener_inventario_actual()
    except Exception as e:
        inventario = {}
    return render_template('pacientes.html', inventario=inventario, usuario=session.get('usuario'))

@app.route('/web/registrar', methods=['POST'])
def web_registrar():
    try:
        ficha = repository.registrar_evento(request.form, session.get('usuario'))
        return redirect(url_for('index', exito=f"Operación exitosa: Ficha {ficha} registrada."))
    except Exception as e:
        return redirect(url_for('index', error=str(e)))

application = app

if __name__ == '__main__':
    app.run(debug=True, port=5000)