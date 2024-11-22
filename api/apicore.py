from functools import wraps
from bdd import db_config
import mysql.connector
from flask import Flask, render_template, jsonify, request, redirect, url_for, session, make_response
from userlog import encriptar_password, guardar_usuario_en_db, login, generar_token, enviar_correo_confirmacion, loginsso, guardar_usuario_en_db_sso
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import uuid
from datetime import datetime
from flask import jsonify, request, session
import requests

def get_user_email():
    # Recibe el token de Google del frontend
    data = request.json
    token = data.get("token")

    if not token:
        return jsonify({"error": "Token no proporcionado"}), 400

    # Consulta a la API de Google para obtener la información del usuario
    try:
        google_user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.get(google_user_info_url, headers=headers)

        # Verifica que la respuesta sea exitosa
        if response.status_code == 200:
            user_info = response.json()
            email = user_info.get("email")

            # Llamar a loginsso y verificar si el usuario está en la base de datos
            login_response = loginsso(email)

            # Si loginsso retorna un 404, guardamos el usuario en la base de datos
            if login_response.status_code == 404:
                guardar_usuario_en_db_sso(email)
                return jsonify({"message": "Usuario no encontrado. Usuario creado con éxito."}), 201
            else:
                # Si el login es exitoso, retornamos la respuesta de loginsso
                return login_response
        else:
            return jsonify({"error": "Error al obtener información del usuario desde Google"}), 500

    except requests.RequestException as e:
        return jsonify({"error": "Error de conexión con Google API"}), 500

def requiere_session(func):
    @wraps(func)
    def decorador(*args, **kwargs):
        # Verifica si 'userid' está en la sesión
        if 'userid' not in session:
            response = make_response(
                jsonify(message="Requiere inicio de sesión", status="Unauthorized"), 
                401
            )
            # Borrar cookies específicas
            response.set_cookie('nombre', '', expires=0, path='/')
            response.set_cookie('direccion', '', expires=0, path='/')
            return response

        return func(*args, **kwargs)
    
    return decorador

def registro():
    data = request.get_json()
    print(data)
    email = data.get('correo')
    password = data.get('contraseña')

    if not email or not password:
        return jsonify({'error': 'Email y contraseña requeridos.'}), 400

    hashed_password = encriptar_password(password)
    try:
        token_generado = generar_token()
        print(token_generado)
        guardar_usuario_en_db(email, hashed_password, token_generado)
        
        enviar_correo_confirmacion(email, token_generado)
        return jsonify({'message': 'Usuario registrado con éxito.'})
    except mysql.connector.IntegrityError as e:
        error_message = str(e)
        if 'Duplicate entry' in error_message:
            return jsonify({'error': 'El correo electrónico ya está registrrado.'}), 409
        else:
            return jsonify({'error': 'Ocurrió un error al crear la cuenta.'}), 500
