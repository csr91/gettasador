from bs4 import BeautifulSoup as bs
import requests
import datetime
import numpy as np
import re

def main():
    pages = 1
    data = []
    done = False
    
    for i in range(1, pages + 1):
        response = requests.get("https://www.argenprop.com/casas-o-departamentos-o-ph/venta/capital-federal?orden-masnuevos&pagina-" + str(i), headers={'User-Agent': 'Chrome'})
        soup = bs(response.text, 'html5lib')
        listings = soup.find_all('div', class_=lambda x: x == 'listing__item' if x else False)

        if done:
            break

        print(f'Scrapeando la página {i}...')
            
        for listing in listings:
            id_ = listing.find('a')
            if id_:
                id_ = id_.get('data-item-card')
            else:
                continue

            link = 'argenprop.com' + listing.find('a').get('href')
            direccion = listing.find(class_="card__address").text.strip()
            
            # Eliminar cualquier texto a la derecha del número, comenzando desde el final
            direccion = re.sub(r"^.*?(\d+.*)$", r"\1", direccion[::-1])[::-1]

            # Reemplazar espacios dobles por un solo espacio
            direccion = re.sub(r"\s{2,}", " ", direccion)

            direccion = re.sub(r", P.*$", "", direccion)
            
            titulo = listing.find(class_="card__title").text.strip()
            descripcion = listing.find(class_="card__info").text.strip()

            if 'Casa' in listing.find(class_="card__title--primary").text:
                # Procesa la ubicación para Casa
                ubicacion = listing.find(class_="card__title--primary").text[18:].split(', ')
                
                if ubicacion[-1] == 'Capital Federal':
                    barrio = ubicacion[0]
                    sub_barrio = np.nan
                else:
                    barrio = ubicacion[-1]
                    sub_barrio = ubicacion[0]

            # Caso para Departamento (Dpto)
            elif 'Departamento' in listing.find(class_="card__title--primary").text:
                # Procesa la ubicación para Departamento
                ubicacion = listing.find(class_="card__title--primary").text[26:].split(', ')
                
                if ubicacion[-1] == 'Capital Federal':
                    barrio = ubicacion[0]
                    sub_barrio = np.nan
                else:
                    barrio = ubicacion[-1]
                    sub_barrio = ubicacion[0]
            
            # Verifica si es un PH
            elif 'PH' in listing.find(class_="card__title--primary").text:
                # Procesa la ubicación para PH
                ubicacion = listing.find(class_="card__title--primary").text[16:].split(', ')
                
                if ubicacion[-1] == 'Capital Federal':
                    barrio = ubicacion[0]
                    sub_barrio = np.nan
                else:
                    barrio = ubicacion[-1]
                    sub_barrio = ubicacion[0]


            precio = listing.find(class_="card__price").text.strip().split(' ')[1]

            moneda = listing.find(class_="card__currency")
            moneda = moneda.text.strip() if moneda else np.nan

            expensas = listing.find(class_="card__expenses")
            expensas = expensas.text.strip() if expensas else np.nan

            superficie = listing.find(class_="icono-superficie_cubierta")
            superficie = superficie.find_parent().find('span').text.strip() if superficie else np.nan

            dormitorios = listing.find(class_="icono-cantidad_dormitorios")
            dormitorios = dormitorios.find_parent().find('span').text.strip() if dormitorios else np.nan

            antiguedad = listing.find(class_="icono-antiguedad")
            antiguedad = antiguedad.find_parent().find('span').text.strip() if antiguedad else np.nan

            banos = listing.find(class_="icono-cantidad_banos")
            banos = banos.find_parent().find('span').text.strip() if banos else np.nan

            data.append([id_, link, direccion, sub_barrio, precio, moneda, superficie, dormitorios, antiguedad, banos])

    # Imprimir los resultados
    for entry in data:
        print(entry)

    if not data:
        print('No se encontraron publicaciones nuevas.')
    else:
        print(f'Se encontraron {len(data)} publicaciones nuevas.')

    return
    
if __name__ == '__main__':
    main()
