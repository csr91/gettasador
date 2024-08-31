from flask import Flask, request, jsonify
import requests
import urllib.parse
import math

app = Flask(__name__)

# Función para convertir metros a grados
def metros_a_grados(metros, latitud):
    grados_latitud = metros / 111320
    grados_longitud = metros / (111320 * abs(math.cos(math.radians(latitud))))
    return grados_latitud, grados_longitud

def cortar_a_6_decimales(numero):
    return float(str(numero)[:str(numero).find('.') + 7])

@app.route('/api/in_calc', methods=['POST'])
def in_calc():
    data = request.get_json()
    direccion = data.get('direccion')
    roundmeters = data.get('roundmeters')

    if not direccion or not isinstance(roundmeters, int):
        return jsonify({'error': 'Datos inválidos'}), 400

    # Codificar la dirección para su uso en la URL
    direccion_codificada = urllib.parse.quote(direccion)

    # URL de la API con la dirección codificada
    url = f"https://apis.datos.gob.ar/georef/api/direcciones?direccion={direccion_codificada}&provincia=CABA"

    try:
        # Hacer la solicitud GET a la API
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        if data['cantidad'] > 0:
            ubicacion = data['direcciones'][0]['ubicacion']
            latitud = ubicacion['lat']
            longitud = ubicacion['lon']
            mapurl = f"https://www.google.com/maps/search/?api=1&query={latitud},{longitud}"

            desplazamiento_latitud, desplazamiento_longitud = metros_a_grados(roundmeters, latitud)
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

            auth_response = requests.post(auth_url, headers=headers, data=data)
            auth_response.raise_for_status()
            token_info = auth_response.json()
            access_token = token_info['access_token']

            # Realizar la primera búsqueda para obtener el total de resultados
            search_url_base = (
                f"https://api.mercadolibre.com/sites/MLA/search?item_location="
                f"lat:{cortar_a_6_decimales(punto_sur_este[0])}_{cortar_a_6_decimales(punto_norte_oeste[0])},"
                f"lat:{cortar_a_6_decimales(punto_norte_oeste[1])}_{cortar_a_6_decimales(punto_sur_este[1])}&category=MLA1459"
            )

            search_response = requests.get(f"{search_url_base}&limit=1&offset=0", headers={'Authorization': f'Bearer {access_token}'})
            search_response.raise_for_status()
            search_data = search_response.json()
            total_results = search_data['paging']['primary_results']

            results = []
            limit = 10
            offset = 0
            current_page = 1
            
            while offset < total_results:
                paginated_url = f"{search_url_base}&limit={limit}&offset={offset}"
                paginated_response = requests.get(paginated_url, headers={'Authorization': f'Bearer {access_token}'})
                paginated_response.raise_for_status()
                paginated_data = paginated_response.json()

                for result in paginated_data['results']:
                    operation = next((attr['value_name'] for attr in result.get('attributes', []) if attr['id'] == 'OPERATION'), 'No disponible')
                    title = result['title']
                    if operation == 'Venta':
                        price = result['price']
                        permalink = result['permalink']
                        address = result['location'].get('address_line', 'No disponible')
                        latitude = result['location'].get('latitude', 'No disponible')
                        longitude = result['location'].get('longitude', 'No disponible')
                        surface_total = next((attr['value_name'] for attr in result.get('attributes', []) if attr['id'] == 'TOTAL_AREA'), 'No disponible')

                        results.append({
                            'title': title,
                            'price': price,
                            'link': permalink,
                            'address': address,
                            'latitude': latitude,
                            'longitude': longitude,
                            'surface_total': surface_total,
                            'operation': operation
                        })
                
                offset += limit
                current_page += 1

            return jsonify({
                'message': f"Centro: Latitud {latitud}, Longitud {longitud}",
                'mapurl': mapurl,
                'results': results
            })

        else:
            return jsonify({'message': 'No se encontraron resultados para la dirección proporcionada.'}), 404

    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
