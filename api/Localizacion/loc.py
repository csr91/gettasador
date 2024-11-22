import requests
import concurrent.futures

def geolocalizar_direccion(direccion, provincia="CABA"):
    
    url = f"https://apis.datos.gob.ar/georef/api/direcciones?direccion={direccion}&provincia={provincia}"

    # Hacer la solicitud GET a la API
    response = requests.get(url)

    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        data = response.json()
        if data['cantidad'] > 0:
            ubicacion = data['direcciones'][0]['ubicacion']
            latitud = ubicacion['lat']
            longitud = ubicacion['lon']
            return latitud, longitud, direccion
        else:
            return None
    else:
        return None


def geolocalizar_multiples_direcciones(direcciones, provincia="CABA"):
    
    resultados = []
    
    # Ejecutar las solicitudes en paralelo
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(geolocalizar_direccion, direccion, provincia) for direccion in direcciones]
        for future in concurrent.futures.as_completed(futures):
            resultado = future.result()
            if resultado:
                resultados.append(resultado)
    
    return resultados