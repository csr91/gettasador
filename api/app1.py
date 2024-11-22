from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
from meli import buscar_propiedades
from Localizacion.loc import geolocalizar_direccion
import json
import requests

def get_connection():
    return mysql.connector.connect(
        host="172.245.184.156",
        user="integracion",
        password="lalita2024",
        database="inmob"
    )

# Tu API key de Google Maps
API_KEY = 'AIzaSyC6sYSWETxfI2noip-BHL6GEZ8QkfC6SeQ'

# Función que obtiene las direcciones sin geolocalización y las geocodifica
def fetch_directions_without_geo():
    try:
        # Obtener la conexión
        connection = get_connection()
        cursor = connection.cursor()

        # Consulta SQL para obtener direcciones sin geolocalización
        query = "SELECT id, direccion FROM avisos WHERE geo IS NULL;"
        cursor.execute(query)

        # Obtener los resultados
        results = cursor.fetchall()

        # Procesar cada dirección
        for row in results:
            aviso_id = row[0]
            direccion = row[1]

            # Geocodificar la dirección usando Google Maps API
            geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={direccion}&key={API_KEY}"
            response = requests.get(geocode_url)

            # Verificar si la solicitud fue exitosa
            if response.status_code == 200:
                data = response.json()

                # Extraer las coordenadas (latitud y longitud) si están disponibles
                if data['status'] == 'OK':
                    lat = data['results'][0]['geometry']['location']['lat']
                    lng = data['results'][0]['geometry']['location']['lng']
                    
                    # Crear el campo 'geo' combinando latitud y longitud
                    geo = f"{lat}, {lng}"

                    # Mostrar log de lo que se va a actualizar
                    print(f"Actualizando ID: {aviso_id}, Dirección: {direccion}, Latitud: {lat}, Longitud: {lng}, Geo: {geo}")
                    
                    # Actualizar la tabla 'avisos' con latitud, longitud y geo
                    update_query = """
                        UPDATE avisos 
                        SET latitud = %s, longitud = %s, geo = %s 
                        WHERE id = %s
                    """
                    cursor.execute(update_query, (lat, lng, geo, aviso_id))
                    connection.commit()
                else:
                    print(f"Error geocodificando la dirección {direccion}: {data['status']}")
            else:
                print(f"Error en la solicitud a Google Maps API: {response.status_code}")
    
    except Exception as e:
        print(f"Error al obtener direcciones: {e}")
    finally:
        # Cerrar el cursor y la conexión
        cursor.close()
        connection.close()

# Llamar a la función
fetch_directions_without_geo()
