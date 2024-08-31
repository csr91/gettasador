from flask import Flask, request, jsonify
from meli import buscar_propiedades

app = Flask(__name__)

@app.route('/api/hello')
def hello():
    return 'Holis'

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
        
        # Devolver los resultados en formato JSON
        return jsonify(resultados), 200
    
    except ValueError:
        return jsonify({'error': 'm2property debe ser un número válido'}), 400
    
    except Exception as e:
        return jsonify({'error': f'Error al procesar la solicitud: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)