import requests
import concurrent.futures

# Lista de direcciones a geolocalizar
direcciones = [
    "Thames 2100", 
    "Humboldt 2300", 
    "Migueletes 2300", 
    "Corrientes 3500", 
    "Santa Fe 1500", 
    "Av. Libertador 5000", 
    "Rivadavia 4500", 
    "Belgrano 2000", 
    "Av. Córdoba 3600", 
    "Pueyrredón 1400"
]

# Función para hacer una solicitud a la API de geolocalización
def geolocalizar_direccion(direccion):
    url = f"https://apis.datos.gob.ar/georef/api/direcciones?direccion={direccion}&provincia=CABA"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data['cantidad'] > 0:
            ubicacion = data['direcciones'][0]['ubicacion']
            latitud = ubicacion['lat']
            longitud = ubicacion['lon']
            return f"Dirección: {direccion} - Latitud: {latitud}, Longitud: {longitud}"
        else:
            return f"No se encontraron resultados para la dirección: {direccion}"
    else:
        return f"Error al hacer la solicitud para la dirección: {direccion} - Código: {response.status_code}"

# Ejecutar solicitudes en paralelo
with concurrent.futures.ThreadPoolExecutor() as executor:
    results = list(executor.map(geolocalizar_direccion, direcciones))

# Imprimir los resultados
for result in results:
    print(result)
