import requests

def geolocalizar_direccion(direccion, provincia="CABA"):
    """
    Función que geolocaliza una dirección utilizando la API de georef.
    
    Args:
        direccion (str): La dirección que se desea geolocalizar.
        provincia (str): La provincia donde se encuentra la dirección (por defecto es 'CABA').
    
    Returns:
        tuple: Una tupla (latitud, longitud) si la geolocalización es exitosa, None si no hay resultados.
    """
    # Codificar la dirección para usar en la URL de la API
    url = f"https://apis.datos.gob.ar/georef/api/direcciones?direccion={direccion}&provincia={provincia}"
    
    # Hacer la solicitud GET a la API
    response = requests.get(url)
    
    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        # Parsear la respuesta JSON
        data = response.json()
        
        # Extraer la geolocalización si está disponible
        if data['cantidad'] > 0:
            ubicacion = data['direcciones'][0]['ubicacion']
            latitud = ubicacion['lat']
            longitud = ubicacion['lon']
            return latitud, longitud
        else:
            print("No se encontraron resultados para la dirección proporcionada.")
            return None
    else:
        print("Error al hacer la solicitud:", response.status_code)
        return None

