import concurrent.futures
import requests
import mysql.connector
import uuid
import json
from flask_cors import CORS
from functools import wraps
from bdd import db_config, get_connection
from flask import Flask, render_template, jsonify, request, redirect, url_for, session, make_response
from userlog import encriptar_password, guardar_usuario_en_db, login, generar_token, enviar_correo_confirmacion, loginsso, guardar_usuario_en_db_sso
from apicore import get_user_email, requiere_session, registro, buscar_propiedades, geolocalizar_direccion, geolocalizar_multiples_direcciones, clean_expired_entries
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, timedelta
from geopy.distance import geodesic

app = Flask(__name__)
app.secret_key = 'calcinmo'
app.config['SECRET_KEY'] = 'calcinmo'
CORS(app)  # Habilitar CORS para todas las rutas

@app.route('/api/save_avisos', methods=['POST'])
def save_aviso():
    try:
        # Obtener los datos enviados en el cuerpo de la solicitud
        avisos = request.json
        
        if not avisos or not isinstance(avisos, list):
            return jsonify({'error': 'Invalid input. Expecting a list of records.'}), 400

        # Extraer las direcciones para geolocalizar
        direcciones = [aviso['direccion_parsed'] for aviso in avisos if aviso.get('direccion_parsed')]

        # Obtener datos de geolocalización en batch
        geo_resultados = geolocalizar_multiples_direcciones(direcciones)

        # Enriquecer avisos con datos de geolocalización
        for aviso in avisos:
            direccion = aviso.get('direccion_parsed')
            geo_data = geo_resultados.get(direccion, {}).get('direcciones', [])

            if geo_data:  # Verifica si la lista de direcciones no está vacía
                ubicacion = geo_data[0].get('ubicacion', {})
                aviso['latitud'] = ubicacion.get('lat', None)
                aviso['longitud'] = ubicacion.get('lon', None)
                aviso['geo'] = f"{ubicacion.get('lat')}, {ubicacion.get('lon')}" if ubicacion.get('lat') and ubicacion.get('lon') else None
            else:
                aviso['latitud'] = None
                aviso['longitud'] = None
                aviso['geo'] = None


        # Conexión a la base de datos
        conn = get_connection()
        cursor = conn.cursor()

        # Consulta SQL con múltiples valores
        sql = """
        INSERT INTO avisos (
            origen, aviso_id, url, direccion, direccion_parsed,
            sub_barrio, barrio, ciudad, provincia, pais,
            precio, moneda, superficie, superficie_cub, ambientes,
            dormitorios, banos, cochera, toilette, antiguedad, 
            disposicion, orientacion, luminosidad, latitud, longitud,
            geo, seller_name, geom
        ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
        %s, %s, %s, %s, %s, %s, %s, 
        CASE 
                WHEN %s IS NOT NULL AND %s IS NOT NULL THEN ST_GeomFromText(CONCAT('POINT(', %s, ' ', %s, ')'), 4326) 
                ELSE NULL 
            END);
        """

        # Preparar los valores a insertar
        values = []
        for aviso in avisos:
            latitud = aviso.get('latitud', None)
            longitud = aviso.get('longitud', None)

            # Añadir los valores a la lista, incluyendo coordenadas como parámetros
            values.append((
                aviso.get('origen', None),
                aviso.get('aviso_id', None),
                aviso.get('url', None),
                aviso.get('direccion', None),
                aviso.get('direccion_parsed', None),
                aviso.get('sub_barrio', None),
                aviso.get('barrio', None),
                aviso.get('ciudad', None),
                aviso.get('provincia', None),
                aviso.get('pais', None),
                aviso.get('precio', None),
                aviso.get('moneda', None),
                aviso.get('superficie', None),
                aviso.get('superficie_cub', None),
                aviso.get('ambientes', None),
                aviso.get('dormitorios', None),
                aviso.get('banos', None),
                aviso.get('cochera', None),
                aviso.get('toilette', None),
                aviso.get('antiguedad', None),
                aviso.get('disposicion', None),
                aviso.get('orientacion', None),
                aviso.get('luminosidad', None),
                latitud,
                longitud,
                aviso.get('geo', None),
                aviso.get('seller_name', None),
                longitud,
                latitud,
                longitud,
                latitud
            ))

        # Ejecutar la consulta en batch
        cursor.executemany(sql, values)
        conn.commit()

        # Cerrar conexión
        cursor.close()
        conn.close()

        return jsonify({'message': f'{len(values)} avisos saved successfully'}), 200

    except mysql.connector.Error as err:
        if conn.is_connected():
            conn.rollback()
        return jsonify({'error': str(err)}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/raw_save_avisos', methods=['POST'])
def raw_save_aviso():
    try:
        # Obtener los datos enviados en el cuerpo de la solicitud
        avisos = request.json
        if not avisos or not isinstance(avisos, list):
            return jsonify({'error': 'Invalid input. Expecting a list of records.'}), 400

        # Conexión a la base de datos
        conn = get_connection()
        cursor = conn.cursor()

        # Consulta SQL con manejo dinámico del campo geom
        sql = """
        INSERT INTO avisos (
            origen, aviso_id, url, direccion, direccion_parsed, 
            sub_barrio, barrio, ciudad, provincia, 
            pais, precio, moneda, superficie, 
            superficie_cub, ambientes, dormitorios, 
            banos, cochera, toilette, antiguedad, 
            disposicion, orientacion, luminosidad, 
            latitud, longitud, geo, meli_category_id, 
            seller_id, seller_name, geom
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s,
            CASE 
                WHEN %s IS NOT NULL AND %s IS NOT NULL THEN ST_GeomFromText(CONCAT('POINT(', %s, ' ', %s, ')'), 4326) 
                ELSE NULL 
            END
        );
        """

        # Preparar los valores a insertar
        values = []
        for aviso in avisos:
            latitud = aviso.get('latitud', None)
            longitud = aviso.get('longitud', None)

            # Añadir los valores a la lista, incluyendo coordenadas como parámetros
            values.append((
                aviso.get('origen', None),
                aviso.get('aviso_id', None),
                aviso.get('url', None),
                aviso.get('direccion', None),
                aviso.get('direccion_parsed', None),
                aviso.get('sub_barrio', None),
                aviso.get('barrio', None),
                aviso.get('ciudad', None),
                aviso.get('provincia', None),
                aviso.get('pais', None),
                aviso.get('precio', None),
                aviso.get('moneda', None),
                aviso.get('superficie', None),
                aviso.get('superficie_cub', None),
                aviso.get('ambientes', None),
                aviso.get('dormitorios', None),
                aviso.get('banos', None),
                aviso.get('cochera', None),
                aviso.get('toilette', None),
                aviso.get('antiguedad', None),
                aviso.get('disposicion', None),
                aviso.get('orientacion', None),
                aviso.get('luminosidad', None),
                latitud,
                longitud,
                aviso.get('geo', None),
                aviso.get('meli_category_id', None),
                aviso.get('seller_id', None),
                aviso.get('seller_name', None),
                longitud,
                latitud,
                longitud,
                latitud
            ))

        # Ejecutar la consulta en batch
        cursor.executemany(sql, values)
        conn.commit()

        # Cerrar conexión
        cursor.close()
        conn.close()

        return jsonify({'message': f'{len(values)} avisos saved successfully'}), 200

    except mysql.connector.Error as err:
        if conn.is_connected():
            conn.rollback()
        return jsonify({'error': str(err)}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500



def generar_poligono_wkt(lat, lon, radio, num_puntos=10):
    """
    Genera un polígono circular en formato WKT alrededor de un punto central.

    Args:
        lat (float): Latitud del punto central.
        lon (float): Longitud del punto central.
        radio (float): Radio del círculo en metros.
        num_puntos (int): Número de puntos para aproximar el círculo.

    Returns:
        str: Polígono en formato WKT.
    """
    puntos = []
    punto_central = (lat, lon)
    angulo_incremento = 360 / num_puntos
    
    for i in range(num_puntos):
        angulo = i * angulo_incremento
        punto = geodesic(meters=radio).destination(punto_central, angulo)
        puntos.append(f"{punto.longitude} {punto.latitude}")
    
    # Cerrar el polígono
    puntos.append(puntos[0])
    
    # Formato WKT: POLYGON((lon1 lat1, lon2 lat2, ..., lon1 lat1))
    return f"POLYGON(({', '.join(puntos)}))"


from mysql.connector import Error

@app.route('/search-polygon', methods=['GET'])
def buscar_puntos_en_poligono():
    """
    Endpoint para buscar puntos dentro de un polígono definido por un punto y un radio.
    """
    try:
        # Obtener parámetros de la solicitud
        punto = request.args.get('point', None)
        radio = request.args.get('distance', None)
        
        if not punto or not radio:
            return jsonify({"error": "Parámetros 'point' y 'distance' son obligatorios"}), 400
        
        # Convertir parámetros
        lat, lon = map(float, punto.split(','))
        radio = float(radio)
        
        # Generar el polígono en formato WKT
        poligono_wkt = generar_poligono_wkt(lat, lon, radio)
        
        # Consultar la base de datos
        connection = get_connection()
        cursor = connection.cursor()
        
        consulta = """
        SELECT direccion, id, geo, ST_AsText(geom) AS geom_text
        FROM avisos
        WHERE ST_Within(geom, ST_GeomFromText(%s, 4326))
        """
        # Ejecutar consulta pasando el polígono como tupla
        cursor.execute(consulta, (poligono_wkt,))
        resultados = cursor.fetchall()
        
        # Cerrar conexión
        cursor.close()
        connection.close()

        return jsonify(resultados), 200
        
    
    except Error as e:
        return jsonify({"error": f"Error en la base de datos: {str(e)}"}), 500
    except ValueError:
        return jsonify({"error": "Formato de parámetros inválido"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/hello')
def hello():
    return 'Holissssss'

@app.route('/api/in_calc', methods=['POST'])
def in_calc():
    rctindex()
    data = request.get_json()
    
    # Extraer los parámetros de la solicitud
    direccion = data.get('direccion')
    m2property = data.get('m2property')
    roundmeters = data.get('roundmeters')
    
    consumo_prestock()

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

@app.route('/api/fullin_calc', methods=['POST'])
def fullin_calc():
    rctindex()
    data = request.get_json()
    
    # Extraer los parámetros de la solicitud
    direccion = data.get('direccion')
    m2property = data.get('m2property')
    roundmeters = data.get('roundmeters')
    
    consumo_prestock()

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

@app.route('/api/sso', methods=['POST'])
def sso():
    return get_user_email()


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
client = MongoClient(uri, server_api=ServerApi('1'))

# Obtener la base de datos y la colección
db = client['gettasador']
collection_disp_ip = db['disp_ip']



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
        # Usuario no está autenticado, buscamos en MongoDB
        existing_entry = collection_disp_ip.find_one({'dispositivo': dispositivo, 'ip': ip})

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
            collection_disp_ip.insert_one(new_entry)

            response_data = {
                'status': 'Unauthorized',
                'message': 'Usuario no autenticado',
                'prestock': 1,
                'dispositivo': dispositivo,
                'ip': ip
            }

        return jsonify(response_data), 401

@app.route('/api/consumo_prestock', methods=['GET'])
def consumo_prestock():
    # Llamamos a rctindex para obtener la respuesta
    response, status_code = rctindex()

    if status_code == 401:
        # Usuario no autenticado
        response_json = response.get_json()
        uuid_to_check = response_json.get('uuid')

        if uuid_to_check:
            # Buscar en MongoDB
            entry = collection_disp_ip.find_one({'idunico': uuid_to_check})

            if entry:
                # Cambiar el prestock a 0
                collection_disp_ip.update_one({'idunico': uuid_to_check}, {'$set': {'prestock': 0}})
                return jsonify({'status': 'OK', 'message': 'Prestock consumido', 'uuid': uuid_to_check}), 200
            else:
                return jsonify({'status': 'Not Found', 'message': 'UUID no encontrado'}), 404
        else:
            return jsonify({'status': 'Error', 'message': 'No UUID in response from rctindex'}), 400
    else:
        # Usuario autenticado u otra respuesta de rctindex
        return jsonify({'status': 'Error', 'message': 'Operación no permitida para usuarios autenticados'}), 403

# Enviar un ping para confirmar una conexiónexitosa
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

if __name__ == '__main__':
    app.run(debug=True)
