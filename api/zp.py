from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Configuración de opciones para el navegador
chrome_options = Options()

chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Ruta al ChromeDriver
chrome_driver_path = "./chromedriver.exe"  # Ruta correcta si está en la misma carpeta que el script

# Inicializar el servicio de ChromeDriver
service = Service(chrome_driver_path)

# Inicializar el navegador
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Abrir la página de ZonaProp
    url = "https://www.zonaprop.com.ar/departamentos-venta-capital-federal-orden-publicado-descendente.html"
    driver.get(url)

    # Obtener el HTML de la página
    page_html = driver.page_source

    # Puedes guardar el HTML en un archivo si lo deseas
    with open("zonaprop_page.html", "w", encoding="utf-8") as file:
        file.write(page_html)

    print("HTML copiado exitosamente.")
finally:
    # Cerrar el navegador
    driver.quit()

soup = BeautifulSoup(page_html, 'html.parser')

# Buscar todos los divs que contienen la clase 'CardContainer-sc-1tt2vbg-5'
cards = soup.find_all('div', class_='CardContainer-sc-1tt2vbg-5')

# Iterar sobre cada tarjeta encontrada
for card in cards:

    dataid = card.find('div', {'data-id': True})
    if dataid:
        id = dataid['data-id']

    posting_div = card.find('div', {'data-to-posting': True})    
    if posting_div:
        full_url = "https://www.zonaprop.com.ar" + posting_div['data-to-posting']

    direccion = card.find(class_="LocationAddress-sc-ge2uzh-0").text.strip()

    sub_barrio = card.find(class_="LocationLocation-sc-ge2uzh-2").text.strip().split(",")[0]

    precio = card.find(class_="Price-sc-12dh9kl-3").text.strip().split(" ")[1]
    

    moneda = card.find(class_="Price-sc-12dh9kl-3").text.strip().split(" ")[0]

    # Encuentra el contenedor principal
    main_features_block = card.find(class_="PostingMainFeaturesBlock-sc-1uhtbxc-0")

    # Encuentra todos los elementos span dentro del contenedor
    spans = main_features_block.find_all("span")[0:2]

    primer_span = spans[0]
    superficie = primer_span.text.strip().split(" ")[0]    

    segundo_span = spans[1]
    ambs = segundo_span.text.strip().split(" ")[0]

    print(id, full_url, direccion, sub_barrio, precio, moneda, superficie, ambs)

