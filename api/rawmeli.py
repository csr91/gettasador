import time
import requests
import urllib.parse
import math

# Función para convertir metros a grados
def metros_a_grados(metros, latitud):
    grados_latitud = metros / 111320
    grados_longitud = metros / (111320 * abs(math.cos(math.radians(latitud))))
    return grados_latitud, grados_longitud

def cortar_a_6_decimales(numero):
    return float(str(numero)[:str(numero).find('.') + 7])

# Solicitar la dirección al usuario
direccion = input("Introduce la dirección: ")
metros = int(input("Distancia en metros a buscar?: "))

print("-" * 40)

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

            time.sleep(1.5)
            print("Calculando Geolocalización:")
            time.sleep(1.5)

            print(f"Centro: Latitud {latitud}, Longitud {longitud}")
            print(f"Mapa: {mapurl}")

            time.sleep(1.5)

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

            response = requests.get(f"{search_url_base}&limit=1&offset=0", headers={'Authorization': f'Bearer {access_token}'})
            print("-" * 40)

            if response.status_code == 200:
                
                data = response.json()
                total_results = data['paging']['primary_results']
                print(f"Total de resultados: {total_results}")
                time.sleep(1.5)
                total_pages = math.ceil(total_results / 50)  # Número total de páginas
                
                # Procesar los resultados paginados
                limit = 50
                offset = 0
                current_page = 1
                
                while offset < total_results:
                    paginated_url = f"{search_url_base}&limit={limit}&offset={offset}"
                    response = requests.get(paginated_url, headers={'Authorization': f'Bearer {access_token}'})

                    if response.status_code == 200:
                        data = response.json()
                        print(f"Página {current_page} de {total_pages}")
                        print("-" * 40)
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
                                surface_total = next((attr['value_name'] for attr in result.get('attributes', []) if attr['id'] == 'TOTAL_AREA'), 'No disponible')

                                print(f"Título: {title}")
                                print(f"Precio: {price}")
                                print(f"Link: {permalink}")
                                print(f"Dirección: {address}")
                                print(f"Geolocalización: Latitud {latitude}, Longitud {longitude}")
                                print(f"Superficie Total: {surface_total} m²")
                                print(f"Operación: {operation}")
                                print("-" * 40)
                    
                    offset += limit
                    current_page += 1
                    time.sleep(1)  # Pausa entre solicitudes para no sobrecargar la API

            else:
                print(f'Error en la solicitud: {response.status_code} - {response.text}')

        else:
            print("No se encontraron resultados para la dirección proporcionada.")
    else:
        print("Error al hacer la solicitud:", response.status_code)

except requests.RequestException as e:
    print("Error en la solicitud:", e)
