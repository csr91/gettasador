import pyautogui
import pyperclip
import time
import random

# Preguntar al usuario cuántas páginas quiere generar
num_pages = int(input("¿Cuántas páginas deseas generar? "))

# Generar las URLs con base en el número de páginas ingresado
base_url = "https://www.zonaprop.com.ar/departamentos-venta-capital-federal-orden-publicado-descendente-pagina-"
start_page = 1  # Cambia este valor para comenzar desde la página 5
urls = [f"{base_url}{i}.html" for i in range(start_page, start_page + num_pages + 1)]

# Imprimir las URLs generadas
print(urls)

# Esperar antes de comenzar
time.sleep(3)

for url in urls:

    print(url)
    # Copiar la URL al portapapeles
    pyperclip.copy(url)

    # Simular Ctrl + L (enfocar la barra de direcciones)
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.1)

    # Simular Ctrl + V (pegar la URL)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.1)

    # Presionar Enter para ir a la URL
    pyautogui.press('enter')
    time.sleep(2)  # Esperar a que la página cargue

    # Realizar un desplazamiento de mouse aleatorio (scroll)
    scroll_amount = random.randint(-800, 300)  # Cambiar el rango según sea necesario
    pyautogui.scroll(scroll_amount)
    time.sleep(2)  # Esperar un momento después de hacer scroll

    # Abrir la consola del navegador
    pyautogui.hotkey('ctrl', 'shift', 'j')
    time.sleep(0.5)

    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.5)

    # Comando para extraer información de las tarjetas de propiedad
    command = """
const cards = document.querySelectorAll('.CardContainer-sc-1tt2vbg-5'); // Reemplaza con el selector adecuado

let results = [];  // Arreglo para almacenar resultados

cards.forEach(card => {
    // Obtener el data-id
    const dataid = card.querySelector('div[data-id]');
    const id = dataid ? dataid.getAttribute('data-id') : null;

    // Obtener el full_url
    const posting_div = card.querySelector('div[data-to-posting]');
    const full_url = posting_div ? "https://www.zonaprop.com.ar" + posting_div.getAttribute('data-to-posting') : null;

    // Obtener dirección
    const direccion = card.querySelector('.LocationAddress-sc-ge2uzh-0') ? card.querySelector('.LocationAddress-sc-ge2uzh-0').innerText.trim() : null;

    // Obtener información de la clase que contiene el barrio y sub-barrio
    const locationData = card.querySelector('.LocationLocation-sc-ge2uzh-2') ? card.querySelector('.LocationLocation-sc-ge2uzh-2').innerText.trim() : null;

    let barrio = null;
    let sub_barrio = null;

    // Verificar si locationData contiene información
    if (locationData) {
        if (locationData.includes("Capital Federal")) {
            // Si es "Capital Federal", barrio es el dato a la izquierda de la coma
            barrio = locationData.split(",")[0].trim();
        } else {
            // Si NO es "Capital Federal", barrio es el dato a la derecha de la coma
            barrio = locationData.split(",")[1].trim();
            // sub_barrio es el dato a la izquierda de la coma
            sub_barrio = locationData.split(",")[0].trim();
        }
    }

    // Obtener precio y moneda
    const precioElement = card.querySelector('.Price-sc-12dh9kl-3');
    let precio = precioElement ? precioElement.innerText.trim().split(" ")[1] : null;
    const moneda = precioElement ? precioElement.innerText.trim().split(" ")[0] : null;

    // Procesar el precio para quitar separadores de miles y reemplazar coma por punto
    if (precio) {
        precio = precio.replace(/\./g, '').replace(',', '.'); // Elimina puntos y cambia coma a punto
    }

    // Obtener características del inmueble
    const main_features_block = card.querySelector('.PostingMainFeaturesBlock-sc-1uhtbxc-0');
    const spans = main_features_block ? main_features_block.querySelectorAll('span') : [];

    // Crear un objeto para almacenar las características
    let features = {
        superficie: null,
        ambientes: null,
        dormitorios: null,
        banos: null,
        cochera: false  // Valor predeterminado: sin cochera (false)
    };

    // Iterar sobre los spans para identificar las características
    spans.forEach(span => {
        let text = span.innerText.toLowerCase();
        if (text.includes('m²')) {
            features.superficie = text.split(" ")[0]; // Superficie
        } else if (text.includes('amb.')) {
            features.ambientes = text.split(" ")[0]; // Ambientes
        } else if (text.includes('dorm.')) {
            features.dormitorios = text.split(" ")[0]; // Dormitorios
        } else if (text.includes('baño') || text.includes('baños')) {
            features.banos = text.split(" ")[0]; // Baños
        } else if (text.includes('coch.')) {
            features.cochera = true;  // Si encuentra la palabra "coch.", asumimos que tiene cochera
        }
    });

    // Crear el objeto con toda la información de la propiedad
    let property = {
        id: id,
        url: full_url,
        location: {
            address: direccion,
            barrio: barrio,
            sub_barrio: sub_barrio
        },
        price: {
            amount: precio,
            currency: moneda
        },
        features: {
            superficie: features.superficie,
            ambientes: features.ambientes,
            dormitorios: features.dormitorios,
            banos: features.banos,
            cochera: features.cochera // Este valor será true o false
        }
    };

    // Agregar la propiedad al array de resultados
    results.push(property);
});

// Enviar todos los resultados en un solo POST después de procesar todas las tarjetas
fetch('http://127.0.0.1:5000/api/save_avisos', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(results)
})
.then(response => response.json())
.then(data => console.log('Datos guardados:', data))
.catch(error => console.error('Error al guardar los datos:', error));

"""

     # Pegar el comando en la consola
    pyperclip.copy(command)

    # Simular Ctrl + V para pegar el comando
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)

    # Presionar Enter para ejecutar el comando
    pyautogui.press('enter')
    time.sleep(0.1)


    pyautogui.hotkey('ctrl', 'shift', 'j')

    # Esperar un momento para que se ejecute el comando y se copien los datos
    time.sleep(1)
    

# Finalizar el script
print("Todas las URLs han sido procesadas.")
