import concurrent.futures
import requests
import mysql.connector
from flask_cors import CORS
from meli import buscar_propiedades
from Localizacion.loc import geolocalizar_direccion, geolocalizar_multiples_direcciones
import json
from functools import wraps
from bdd import db_config
from flask import Flask, render_template, jsonify, request, redirect, url_for, session, make_response
from userlog import encriptar_password, guardar_usuario_en_db, login, generar_token, enviar_correo_confirmacion, loginsso, guardar_usuario_en_db_sso
from apicore import get_user_email, requiere_session, registro
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'calcinmo'
app.config['SECRET_KEY'] = 'calcinmo'
CORS(app)  # Habilitar CORS para todas las rutas

# Función para obtener una nueva conexión a la base de datos
def get_connection():
    return mysql.connector.connect(
        host="172.245.184.156",
        user="integracion",
        password="lalita2024",
        database="inmob"
    )

@app.route('/api/hello')
def hello():
    return 'Holissssss'

@app.route('/api/in_calc', methods=['POST'])
def in_calc():
    # Obtener los datos JSON de la solicitud
    data = request.get_json()
    print(data)
    
    # Extraer los parámetros de la solicitud
    direccion = data.get('direccion')
    m2property = data.get('m2property')
    roundmeters = data.get('roundmeters')
    
    if not direccion or m2property is None or roundmeters is None:
        return jsonify({'error': 'Faltan parámetros: direccion, m2property, y roundmeters son requeridos'}), 400
    
    try:
        # Convertir m2property a float
        m2property = float(m2property)
        
        # Llamar a la función buscar_propiedades
        resultados = buscar_propiedades(direccion, roundmeters)
        print(resultados)
        
        if 'error' in resultados:
            return jsonify({'error': resultados['error']}), 400
        
        # Obtener y redondear m2price_average
        m2price_average = resultados.get('m2price_average')
        m2price_count = resultados.get('m2price_count')
        
        if m2price_average is None or not isinstance(m2price_average, (int, float)):
            return jsonify({'error': 'm2price_average no encontrado o no es un número válido'}), 400
        
        m2price_average = round(m2price_average, 2)
        
        # Multiplicar m2property por m2price_average
        total_price = m2property * m2price_average
        
        # Agregar el resultado de la multiplicación a los resultados con el mensaje personalizado
        resultados['mensaje'] = f"Encontramos {m2price_count} resultados con un precio promedio de {m2price_average} por m2, tu propiedad de {m2property} m2 tiene una valuación aproximada de: {round(total_price)} USD"
        
        resultados['total_price'] = round(total_price)

        # Devolver los resultados en formato JSON
        return jsonify(resultados), 200
    
    except ValueError:
        return jsonify({'error': 'm2property debe ser un número válido'}), 400
    
    except Exception as e:
        return jsonify({'error': f'Error al procesar la solicitud: {str(e)}'}), 500

# Contador de llamadas al endpoint
call_count = 0

@app.route('/api/save_avisos', methods=['POST'])
def save_aviso():
    global call_count  # Usar la variable global para el contador

    try:
        # Incrementar el contador
        call_count += 1
        print(call_count)

        # Si el contador llega a 5, llamar a la función fetch_directions_without_geo en paralelo
        # if call_count >= 5:
        #     with concurrent.futures.ThreadPoolExecutor() as executor:
        #         executor.submit(fetch_directions_without_geo)
        #     call_count = 0

        # Obtener los datos del cuerpo de la solicitud
        data_list = request.json  # Se espera una lista de diccionarios
        
        # Lista para almacenar los avisos guardados y errores
        saved_avisos = []
        errors = []

        # Establecer conexión a la base de datos
        conn = get_connection()
        cursor = conn.cursor()

        # Definir la consulta SQL para insertar datos
        sql = """
        INSERT INTO avisos (origen, aviso_id, url, direccion, direccion_parsed, 
                            sub_barrio, barrio, ciudad, provincia, 
                            pais, precio, moneda, superficie, 
                            superficie_cub, ambientes, dormitorios, 
                            banos, cochera, toilette, antiguedad, 
                            disposicion, orientacion, luminosidad, 
                            latitud, longitud, geo) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        # Dividir data_list en grupos de 10
        for i in range(0, len(data_list), 10):
            batch = data_list[i:i + 10]
            direcciones = [data['direccion'] for data in batch if 'direccion' in data]

            # Llamar a la función de geolocalización múltiple
            resultados_geo = geolocalizar_multiples_direcciones(direcciones)

            # Crear un diccionario para mapear direcciones a resultados de geolocalización
            geo_map = {direccion: (latitud, longitud) for latitud, longitud, direccion in resultados_geo}

            # Procesar cada aviso en el batch
            for data in batch:
                # Verificar que se recibieron los campos requeridos
                required_fields = ['origen', 'aviso_id', 'url', 'direccion']

                # Variable para rastrear si hay errores
                has_error = False
                
                # Validar campos
                for field in required_fields:
                    if field not in data or data[field] is None or data[field] == "":
                        errors.append(f"Falta el campo o el valor es inválido: {field} en aviso_id {data.get('aviso_id')}")
                        has_error = True  # Marcar que hay un error
                        break  # Salir del bucle si hay un error en el aviso
                
                # Validar el precio si está presente y solo si no hay errores
                if not has_error and 'precio' in data and data['precio'] is not None:
                    try:
                        float(data['precio'])  # Intentar convertir a float
                    except ValueError:
                        errors.append(f"El precio debe ser un número válido en aviso_id {data.get('aviso_id')}")
                        has_error = True  # Marcar que hay un error
                elif not has_error:
                    errors.append(f"Falta el campo 'precio' o su valor es inválido en aviso_id {data.get('aviso_id')}")
                    has_error = True  # Marcar que hay un error

                # Si hay un error, continuar con el siguiente aviso
                if has_error:
                    continue
                
                # Obtener latitud y longitud del mapa de geolocalización
                lat_long_geo = geo_map.get(data['direccion'])
                if lat_long_geo:
                    latitud, longitud = lat_long_geo
                    geo = f"{latitud}, {longitud}"  # Concatenar latitud y longitud
                else:
                    latitud, longitud, geo = None, None, None  # Manejar el caso donde no se pudo obtener

                # Ejecutar la consulta con los valores recibidos
                cursor.execute(sql, (
                    data['origen'], 
                    data['aviso_id'], 
                    data['url'], 
                    data.get('direccion'),  
                    data.get('direccion_parsed'),
                    data.get('sub_barrio'),
                    data.get('barrio'),
                    data.get('ciudad'),
                    data.get('provincia'),
                    data.get('pais'),
                    data.get('precio'),
                    data.get('moneda'),
                    data.get('superficie'),
                    data.get('superficie_cub'),
                    data.get('ambientes'),
                    data.get('dormitorios'),
                    data.get('banos'),
                    data.get('cochera'),
                    data.get('toilette'),
                    data.get('antiguedad'),
                    data.get('disposicion'),
                    data.get('orientacion'),
                    data.get('luminosidad'),
                    latitud,  # Valor obtenido de geolocalización
                    longitud,  # Valor obtenido de geolocalización
                    geo  # Valor concatenado
                ))
                saved_avisos.append(data['aviso_id'])  # Agregar el aviso_id guardado a la lista

            # Confirmar los cambios después de procesar el batch
            conn.commit()

        # Cerrar la conexión
        cursor.close()
        conn.close()

        # Preparar respuesta
        response = {
            "message": "Avisos procesados.",
            "saved_avisos": saved_avisos,
            "errors": errors
        }
        print(response)
        
        return jsonify(response), 201 if not errors else 207  # 207 si hay advertencias (errores pero procesados)

    except mysql.connector.Error as err:
        print(err)
        return jsonify({"error": str(err)}), 500
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


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

@app.route('/api/sso', methods=['POST'])
def sso():
    return get_user_email()

# Variable en memoria para almacenar datos de dispositivo e IP
disp_ip = []

# Función para limpiar entradas expiradas
def clean_expired_entries():
    global disp_ip
    current_time = datetime.now()
    disp_ip = [entry for entry in disp_ip if entry['endtime'] > current_time]

# Endpoint para manejar sesiones de usuario y disp_ip
@app.route('/api/getsession', methods=['GET'])
def rctindex():
    clean_expired_entries()
    dispositivo = request.headers.get('User-Agent', 'Unknown')
    ip = request.remote_addr
    user_id = session.get('userid')

    if user_id:
        # Usuario está autenticado
        response_data = {
            'status': 'OK',
            'message': 'Usuario autenticado',
            'user_id': user_id
        }
        return jsonify(response_data), 200
    else:
        # Usuario no está autenticado
        existing_entry = next((entry for entry in disp_ip if entry['dispositivo'] == dispositivo and entry['ip'] == ip), None)

        if existing_entry:
            # Registro ya existe, agregamos uuid y prestock al response
            response_data = {
                'status': 'Unauthorized',
                'message': 'Usuario no autenticado',
                'prestock': existing_entry['prestock'],
                'uuid': existing_entry['idunico'],
                'dispositivo': dispositivo,
                'ip': ip
            }
        else:
            # Creamos un nuevo registro
            new_entry = {
                'idunico': str(uuid.uuid4()),
                'dispositivo': dispositivo,
                'ip': ip,
                'prestock': 1,
                'endtime': datetime.now() + timedelta(seconds=30)
            }
            disp_ip.append(new_entry)

            response_data = {
                'status': 'Unauthorized',
                'message': 'Usuario no autenticado',
                'prestock': 1,
                'dispositivo': dispositivo,
                'ip': ip
            }

        return jsonify(response_data), 401

@app.route('/api/consumo_prestock', methods=['POST'])
def consumo_prestock():
    print(disp_ip)
    # Llamamos a rctindex para obtener la respuesta
    response, status_code = rctindex()
    
    if status_code == 401:
        # Usuario no autenticado
        response_json = response.get_json()
        uuid_to_check = response_json.get('uuid')
        
        if uuid_to_check:
            print(f"UUID obtenido de rctindex: {uuid_to_check}")
            # Buscar en disp_ip
            entry = next((entry for entry in disp_ip if entry['idunico'] == uuid_to_check), None)

            if entry:
                # Cambiar el prestock a 0
                entry['prestock'] = 0
                return jsonify({'status': 'OK', 'message': 'Prestock consumido', 'uuid': uuid_to_check}), 200
            else:
                return jsonify({'status': 'Not Found', 'message': 'UUID no encontrado'}), 404
        else:
            return jsonify({'status': 'Error', 'message': 'No UUID in response from rctindex'}), 400
    else:
        # Usuario autenticado u otra respuesta de rctindex
        return jsonify({'status': 'Error', 'message': 'Operación no permitida para usuarios autenticados'}), 403
    

@app.route('/api/login', methods=['POST'])
def pstlogin():
    return login()

@app.route('/api/registro', methods=['POST'])
def pstregistro():
    return registro()

@app.route('/api/logout', methods=['POST'])
def logout():       
        session.clear()
        session.pop('userid', None)
        session.pop('session', None)
        response = make_response(redirect(url_for('page_inicio')))
        response.delete_cookie('direccion')
        response.delete_cookie('nombre')
        response.delete_cookie('session')
        return response

@app.route('/')
@requiere_session
def page_inicio():
    return 'Página de inicio'

@app.route('/api/logout', methods=['GET'])
def getlogout():       
        session.pop('userid', None)
        session.pop('session', None)
        session.permanent = False
        response = make_response(redirect(url_for('page_inicio')))
        response.delete_cookie('direccion')
        response.delete_cookie('nombre')
        response.delete_cookie('session')
        return response

@app.route('/api/confirmar_registro', methods=['GET'])
def confirmar_registro():
    token = request.args.get('token')
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    print(token)

    try:
        query = "SELECT idcuenta FROM cuentas WHERE token = %s"
        cursor.execute(query, (token,))
        cuenta = cursor.fetchone()
        print(cuenta)

        if cuenta:
            update_query = "UPDATE cuentas SET habilitado = 1 WHERE token = %s"
            cursor.execute(update_query, (token,))
            conn.commit()
            session['userid'] = cuenta[0]
            return redirect("/")  # Aquí rediriges a la raíz "/"
        else:
            return jsonify({'message': 'Usuario registrado sin éxito.'})
    finally:
        cursor.close()
        conn.close()

# URI de conexión a MongoDB
uri = "mongodb+srv://cesarmendoza77:7hLCBopqFoTBmF4v@cluster0.papc1wn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Crear un nuevo cliente y conectar al servidor
client = MongoClient(uri, server_api=ServerApi('1'))

# Obtener la base de datos y la colección
db = client['gettalent']
collection_busquedas = db['busquedas']
collection_candidatos = db['candidatos']

# Enviar un ping para confirmar una conexión exitosa
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

if __name__ == '__main__':
    app.run(debug=False)
