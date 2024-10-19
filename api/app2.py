from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

# Función para obtener una nueva conexión a la base de datos
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="inrepair9843",
        database="inmob"
    )

@app.route('/save_avisos', methods=['POST'])
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

    except Exception as e:
        # Manejar otros posibles errores
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        # Asegurarse de cerrar la conexión y el cursor
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(port=5000, debug=True)
