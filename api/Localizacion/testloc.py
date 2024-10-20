# test_geolocalizacion.py

from loc import geolocalizar_direccion

# Probar la función con una dirección
direccion = "Av de la Cruz 6800"
resultado = geolocalizar_direccion(direccion)

if resultado:
    latitud, longitud = resultado
    print(f"Latitud: {latitud}, Longitud: {longitud}")
else:
    print("No se pudo geolocalizar la dirección.")
