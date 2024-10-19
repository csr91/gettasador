from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
from meli import buscar_propiedades

app = Flask(__name__)
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

@app.route('/api/save_avisos', methods=['POST'])
def save_aviso():
    try:
        # Obtener los datos del JSON enviado desde el cliente
        data = request.json
        if not isinstance(data, list):
            return jsonify({"status": "error", "message": "El payload debe ser una lista de avisos"}), 400

        # Establecer conexión con la base de datos
        conn = get_connection()
        cursor = conn.cursor()

        # Consulta SQL para insertar los datos
        query = """
            INSERT INTO avisos (aviso_id, url, direccion, sub_barrio, precio, moneda, superficie, ambientes, dormitorios, banos, cochera)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Iterar sobre la lista de avisos y guardar cada uno
        for aviso in data:
            aviso_id = aviso.get('id')
            url = aviso.get('url')
            direccion = aviso.get('location', {}).get('address')
            sub_barrio = aviso.get('location', {}).get('sub_barrio')
            precio = aviso.get('price', {}).get('amount')
            moneda = aviso.get('price', {}).get('currency')

            # Manejar valores nulos en los campos numéricos con valores por defecto
            superficie = aviso.get('features', {}).get('superficie') or 0
            ambientes = aviso.get('features', {}).get('ambientes') or 0
            dormitorios = aviso.get('features', {}).get('dormitorios') or 0
            banos = aviso.get('features', {}).get('banos') or 0
            cochera = aviso.get('features', {}).get('cochera', False)

            # Convertir valores de tipo string a enteros donde sea necesario
            if isinstance(superficie, str):
                superficie = int(superficie) if superficie.isdigit() else 0
            if isinstance(ambientes, str):
                ambientes = int(ambientes) if ambientes.isdigit() else 0
            if isinstance(dormitorios, str) and dormitorios is not None:
                dormitorios = int(dormitorios) if dormitorios.isdigit() else 0
            if isinstance(banos, str) and banos is not None:
                banos = int(banos) if banos.isdigit() else 0
            cochera = int(cochera) if isinstance(cochera, bool) else 0

            # Ejecutar la consulta para cada aviso
            values = (aviso_id, url, direccion, sub_barrio, precio, moneda, superficie, ambientes, dormitorios, banos, cochera)
            cursor.execute(query, values)

        # Confirmar todos los inserts en la base de datos
        conn.commit()

        # Devolver una respuesta de éxito
        return jsonify({"status": "success", "message": "Avisos guardados correctamente"})

    except mysql.connector.Error as err:
        # Si ocurre un error de MySQL, devolver un mensaje de error
        return jsonify({"status": "error", "message": str(err)}), 500
        print(err)

    except Exception as e:
        # Manejar otros posibles errores
        return jsonify({"status": "error", "message": str(e)}), 500
        print(err)

    finally:
        # Asegurarse de cerrar la conexión y el cursor
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
