from flask import request, jsonify, make_response, session
import hashlib
import datetime
import mysql.connector
import bcrypt
import bdd
from bdd import db_config
import secrets
import smtplib
from email.mime.text import MIMEText

def generar_token():
    token = secrets.token_hex(16)
    return token

def enviar_correo_confirmacion(destinatario, token_generado):
    remitente = 'cesar.mendoza.77@gmail.com'
    contraseña = 'ecjuhpcxlsinwlmb'
    
    # Formatear el cuerpo del mensaje en HTML con el enlace como un botón
    mensaje_html = f'''
    <html>
    <body>
        <p>Hola,</p>
        <p>Gracias por registrarte en geTTalent</p>
        <p></p>
        <p>Por favor, utiliza el siguiente botón para confirmar tu cuenta:</p>
        <a href="http://localhost:3000/api/confirmar_registro?token={token_generado}" style="display:inline-block;padding:10px 20px;background-color:#007BFF;color:#ffffff;text-decoration:none;border-radius:5px;">Confirmar cuenta</a>
    </body>
    </html>
    '''

    # Crear un mensaje MIME con formato HTML
    msg = MIMEText(mensaje_html, 'html')
    msg['Subject'] = 'geTTalent | Confirmación de cuenta'
    msg['From'] = remitente
    msg['To'] = destinatario

    # Configurar el servidor SMTP y enviar el mensaje
    with smtplib.SMTP('smtp.gmail.com', 587) as servidor_smtp:
        servidor_smtp.starttls()
        servidor_smtp.login(remitente, contraseña)
        servidor_smtp.send_message(msg)


def verificar_contraseña(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def obtener_usuario_por_correo(correo):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    query = "select c.Idcuenta,c.mail,c.contraseña_hash,c.habilitado, i.nombre, i.direccion from cuentas c left join infocuentas i on i.idcuenta = c.Idcuenta WHERE mail = %s"
    cursor.execute(query, (correo,))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()
    return usuario

def actualizar_ultima_fecha_inicio_sesion(id_usuario, fecha_actual):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    query = "UPDATE cuentas SET LastLogin = %s WHERE Idcuenta = %s"
    cursor.execute(query, (fecha_actual, id_usuario))
    conn.commit()
    cursor.close()
    conn.close()

def validar_cookie(cookie_value):
    correo = 'usuario'
    fecha_actual = datetime.datetime.now()
    codigo_algoritmico_esperado = hashlib.sha256(f"{correo}{fecha_actual}".encode()).hexdigest()
    return cookie_value == codigo_algoritmico_esperado

def encriptar_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def guardar_usuario_en_db(email, hashed_password, token_generado):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    fecha_creacion = datetime.datetime.now()
    query = "INSERT INTO cuentas (mail, contraseña_hash, token, FechaCreacion) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (email, hashed_password, token_generado, fecha_creacion))
    conn.commit()
    cursor.close()
    conn.close()

def guardar_usuario_en_db_sso(email):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    fecha_creacion = datetime.datetime.now()

    # Consulta para insertar un nuevo usuario con habilitado = 1
    query = "INSERT INTO cuentas (mail, FechaCreacion, habilitado, contraseña_hash) VALUES (%s, %s, %s, %s)"
    sso = encriptar_password('default')
    cursor.execute(query, (email, fecha_creacion, 1, sso))
    conn.commit()
    cursor.close()
    conn.close()

    usuario = obtener_usuario_por_correo(email)
    # Configurar cookies
    fecha_expiracion = datetime.datetime.now() + datetime.timedelta(days=5)
    # response.set_cookie('nombre', f"{nombre}", expires=fecha_expiracion, httponly=False)
    # response.set_cookie('direccion', f"{direccion}", expires=fecha_expiracion, httponly=False)

    # Configurar la sesión para expirar en 7 días
    session.permanent = True
    session['userid'] = usuario
    

def loginsso(email):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Consulta para obtener Idcuenta y habilitado
    query = "SELECT Idcuenta, habilitado FROM cuentas WHERE mail = %s"
    cursor.execute(query, (email,))
    result = cursor.fetchone()

    if result:
        usuario, habilitado = result
        # Si habilitado es 0, lo actualizamos a 1
        if habilitado == 0:
            update_query = "UPDATE cuentas SET habilitado = 1 WHERE Idcuenta = %s"
            cursor.execute(update_query, (usuario,))
            conn.commit()
        
        # Configurar respuesta exitosa
        response = make_response("Inicio de sesión exitoso", 200)
        actualizar_ultima_fecha_inicio_sesion(usuario, datetime.datetime.now())
        
        # Configurar cookies
        fecha_expiracion = datetime.datetime.now() + datetime.timedelta(days=5)
        # response.set_cookie('nombre', f"{nombre}", expires=fecha_expiracion, httponly=False)
        # response.set_cookie('direccion', f"{direccion}", expires=fecha_expiracion, httponly=False)

        # Configurar la sesión para expirar en 7 días
        session.permanent = True
        session['userid'] = usuario

    else:
        # Si el correo no está en la base de datos, retornar un mensaje de error
        response = make_response("Correo electrónico no encontrado", 404)

    cursor.close()
    conn.close()
    return response
    
    

def login():
    data = request.get_json()
    correo = data.get('correo')
    contraseña = data.get('contraseña')
    if not correo or not contraseña:
        return jsonify({'error': 'Correo y contraseña son requeridos.'}), 400
    usuario = obtener_usuario_por_correo(correo)
    if not usuario:
        return jsonify({'error': 'Correo no registrado.'}), 401
    contraseña_hash = usuario[2]
    if not verificar_contraseña(contraseña, contraseña_hash):
        return jsonify({'error': 'Correo o contraseña incorrectos.'}), 401
    if not usuario[3]:
        return jsonify({'error': 'La cuenta no está habilitada.'}), 401
    id_usuario = usuario[0]
    nombre = usuario[4]
    direccion = usuario[5]
    response_data = {
        'message': 'Inicio de sesión exitoso',
        'id': id_usuario
    }
    response = make_response(jsonify(response_data))
    actualizar_ultima_fecha_inicio_sesion(usuario[0], datetime.datetime.now())
    codigo_algoritmico = hashlib.sha256(f"{correo}{datetime.datetime.now()}".encode()).hexdigest()
    fecha_expiracion = datetime.datetime.now() + datetime.timedelta(days=5)
    response.set_cookie('nombre', f"{nombre}", expires=fecha_expiracion, httponly=False)
    response.set_cookie('direccion', f"{direccion}", expires=fecha_expiracion, httponly=False)
    # Configurar la sesión para expirar en 7 días
    session.permanent = True
    session['userid'] = usuario[0]
    return response