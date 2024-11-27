from functools import wraps
from bdd import db_config, get_connection
from flask import Flask, render_template, jsonify, request, redirect, url_for, session, make_response
from userlog import encriptar_password, guardar_usuario_en_db, login, generar_token, enviar_correo_confirmacion, loginsso, guardar_usuario_en_db_sso
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from geopy.distance import geodesic
import uuid
import time
import urllib.parse
import math
import re
import concurrent.futures
import requests
import mysql.connector

# URI de conexión a MongoDB
uri = "mongodb+srv://cesarmendoza77:7hLCBopqFoTBmF4v@cluster0.papc1wn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

# Obtener la base de datos y la colección
db = client['gettasador']
collection_disp_ip = db['disp_ip']

def geolocalizar_direccion(direccion, provincia="CABA"):
    url = f"https://apis.datos.gob.ar/georef/api/direcciones?direccion={direccion}&provincia={provincia}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # Retorna el JSON con los datos de la dirección
    else:
        return {"error": f"Error al consultar {direccion}. Código de estado: {response.status_code}"}

def geolocalizar_multiples_direcciones(direcciones, provincia="CABA"):
    resultados = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(geolocalizar_direccion, direccion, provincia): direccion for direccion in direcciones}
        for future in concurrent.futures.as_completed(futures):
            direccion = futures[future]
            try:
                resultados[direccion] = future.result()
            except Exception as e:
                resultados[direccion] = {"error": str(e)}
    return resultados

# Función para convertir metros a grados
def metros_a_grados(metros, latitud):
    grados_latitud = metros / 111320
    grados_longitud = metros / (111320 * abs(math.cos(math.radians(latitud))))
    return grados_latitud, grados_longitud

def cortar_a_6_decimales(numero):
    return float(str(numero)[:str(numero).find('.') + 7])

def buscar_propiedades(direccion, metros):
    # Codificar la dirección para su uso en la URL
    direccion_codificada = urllib.parse.quote(direccion)

    # URL de la API con la dirección codificada
    url = f"https://apis.datos.gob.ar/georef/api/direcciones?direccion={direccion_codificada}&provincia=CABA"

    try:
        # Hacer la solicitud GET a la API
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            if data['cantidad'] > 0:
                ubicacion = data['direcciones'][0]['ubicacion']
                latitud = ubicacion['lat']
                longitud = ubicacion['lon']
                mapurl = f"https://www.google.com/maps/search/?api=1&query={latitud},{longitud}"
                
                desplazamiento_latitud, desplazamiento_longitud = metros_a_grados(metros, latitud)
                punto_norte_oeste = (latitud + desplazamiento_latitud, longitud - desplazamiento_longitud)
                punto_sur_este = (latitud - desplazamiento_latitud, longitud + desplazamiento_longitud)

                client_id = '382404286946395'
                client_secret = 'kgtQyBQOMsXiQR2YZsjXjbD6E4t8ylnX'

                # Obtener el token de acceso
                auth_url = 'https://api.mercadolibre.com/oauth/token'
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
                data = {
                    'grant_type': 'client_credentials',
                    'client_id': client_id,
                    'client_secret': client_secret
                }

                response = requests.post(auth_url, headers=headers, data=data)
                token_info = response.json()
                access_token = token_info['access_token']

                # Realizar la primera búsqueda para obtener el total de resultados
                search_url_base = (
                    f"https://api.mercadolibre.com/sites/MLA/search?item_location="
                    f"lat:{cortar_a_6_decimales(punto_sur_este[0])}_{cortar_a_6_decimales(punto_norte_oeste[0])},"
                    f"lat:{cortar_a_6_decimales(punto_norte_oeste[1])}_{cortar_a_6_decimales(punto_sur_este[1])}&category=MLA1459"
                )

                print(search_url_base)

                response = requests.get(f"{search_url_base}&limit=1&offset=0", headers={'Authorization': f'Bearer {access_token}'})

                if response.status_code == 200:
                    data = response.json()
                    total_results = data['paging']['primary_results']
                    total_pages = math.ceil(total_results / 50)  # Número total de páginas
                    
                    # Variables acumuladoras para m2price
                    m2price_sum = 0
                    m2price_count = 0
                    
                    # Procesar los resultados paginados
                    limit = 50
                    offset = 0
                    current_page = 1
                    resultados = []
                    
                    while offset < total_results:
                        paginated_url = f"{search_url_base}&limit={limit}&offset={offset}"
                        response = requests.get(paginated_url, headers={'Authorization': f'Bearer {access_token}'})

                        if response.status_code == 200:
                            data = response.json()
                            for result in data['results']:
                                operation = next((attr['value_name'] for attr in result.get('attributes', []) if attr['id'] == 'OPERATION'), 'No disponible')
                                currency = result['currency_id']
                                title = result['title']
                                if operation == 'Venta' and currency == 'USD':
                                    price = result['price']
                                    permalink = result['permalink']
                                    address = result['location'].get('address_line', 'No disponible')
                                    latitude = result['location'].get('latitude', 'No disponible')
                                    longitude = result['location'].get('longitude', 'No disponible')
                                    # Obtener solo el número de `surface_total`
                                    surface_total = next((attr['value_name'] for attr in result.get('attributes', []) if attr['id'] == 'TOTAL_AREA'), 'No disponible')

                                    if surface_total != 'No disponible':
                                        # Usar expresión regular para extraer solo el número
                                        match = re.search(r'\d+\.?\d*', surface_total)
                                        if match:
                                            surface_total = float(match.group())
                                        else:
                                            surface_total = 'No disponible'

                                    # Asegurarse de que tanto price como surface_total sean números válidos antes de calcular m2price
                                    if surface_total != 'No disponible' and price is not None:
                                        try:
                                            surface_total = float(surface_total)
                                            m2price = price / surface_total
                                            
                                            # Sumar m2price y aumentar el contador
                                            m2price_sum += m2price
                                            m2price_count += 1
                                        except (ValueError, ZeroDivisionError):
                                            m2price = 'No disponible'
                                    else:
                                        m2price = 'No disponible'

                                    resultados.append({
                                        'title': title,
                                        'link': permalink,
                                        'price': price,
                                        'address': address,
                                        'surface_total': surface_total,
                                        'm2price': m2price,
                                    })
                        offset += limit
                        current_page += 1
                        time.sleep(1)  # Pausa entre solicitudes para no sobrecargar la API

                    # Calcular el promedio de m2price
                    m2price_average = m2price_sum / m2price_count if m2price_count > 0 else 'No disponible'

                    return {
                        'total_results': total_results,
                        'map_url': mapurl,
                        'm2price_average': m2price_average,
                        'm2price_count': m2price_count
                    }
                else:
                    return {'error': f'Error en la solicitud: {response.status_code} - {response.text}'}
            else:
                return {'error': "No se encontraron resultados para la dirección proporcionada."}
        else:
            return {'error': f"Error al hacer la solicitud: {response.status_code}"}
    except requests.RequestException as e:
        return {'error': f"Error en la solicitud: {e}"}

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

# Tu API key de Google Maps
API_KEY = 'AIzaSyC6sYSWETxfI2noip-BHL6GEZ8QkfC6SeQ'

# Función que obtiene las direcciones sin geolocalización y las geocodifica
def fetch_directions_without_geo():
    try:
        # Obtener la conexión
        connection = get_connection()
        cursor = connection.cursor()

        # Consulta SQL para obtener direcciones sin geolocalización
        query = "SELECT id, direccion FROM avisos WHERE geo IS NULL;"
        
        # Ejecutar la consulta
        cursor.execute(query)

        # Obtener los resultados
        results = cursor.fetchall()

        # Lista para almacenar los IDs actualizados
        updated_ids = []

        # Procesar cada dirección
        for row in results:
            aviso_id = row[0]
            direccion = row[1]

            # Geocodificar la dirección usando Google Maps API
            geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={direccion}, Capital Federal, Argentina&key={API_KEY}"

            # Realizar la solicitud a la API
            response = requests.get(geocode_url)

            # Verificar si la solicitud fue exitosa
            if response.status_code == 200:
                data = response.json()

                # Extraer las coordenadas (latitud y longitud) si están disponibles
                if data['status'] == 'OK':
                    lat = data['results'][0]['geometry']['location']['lat']
                    lng = data['results'][0]['geometry']['location']['lng']
                    
                    # Preparar el valor para el campo 'geo'
                    geo = f"{lat}, {lng}"

                    # Actualizar la tabla con los nuevos datos
                    update_query = """
                    UPDATE avisos
                    SET latitud = %s, longitud = %s, geo = %s
                    WHERE id = %s;
                    """
                    cursor.execute(update_query, (lat, lng, geo, aviso_id))
                    connection.commit()  # Confirmar los cambios en la base de datos

                    # Agregar el ID a la lista de actualizados
                    updated_ids.append(aviso_id)

                else:
                    print(f"Error geocodificando la dirección {direccion}: {data['status']}")
            else:
                print(f"Error en la solicitud a Geocoding API: {response.status_code}")
    
    except Exception as e:
        print(f"Error al obtener direcciones: {e}")
    finally:
        # Cerrar la conexión
        cursor.close()
        connection.close()

        # Imprimir los IDs actualizados al final
        if updated_ids:
            print("Geolocalización actualizada con Geocoding API de Google:")
            print(f"Ids: {updated_ids}")
        else:
            print("No se actualizaron IDs.")

# Función para limpiar entradas expiradas en MongoDB
def clean_expired_entries():
    current_time = datetime.now()
    # Encuentra los documentos que serán eliminados
    expired_entries = collection_disp_ip.find({'endtime': {'$lt': current_time}})
    
    # Extrae y muestra los UUIDs de los documentos a eliminar
    uuids_to_delete = [entry.get('uuid') for entry in expired_entries]
    print("UUIDs a limpiar:", uuids_to_delete)
    
    # Elimina los documentos cuyo campo 'endtime' ya ha pasado
    collection_disp_ip.delete_many({'endtime': {'$lt': current_time}})