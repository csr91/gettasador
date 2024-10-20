import requests

# Definir la dirección que quieres geolocalizar
direccion = "Thames  2100"

# URL de la API con la dirección codificada
url = f"https://apis.datos.gob.ar/georef/api/direcciones?direccion={direccion}&provincia=CABA"

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
        print(f"Latitud: {latitud}, Longitud: {longitud}")
    else:
        print("No se encontraron resultados para la dirección proporcionada.")
else:
    print("Error al hacer la solicitud:", response.status_code)
