import pyautogui
import pyperclip
import time
import random

# Lista de URLs a visitar
urls = [
    "https://www.zonaprop.com.ar/propiedades/clasificado/veclapin-venta-departamento-3-ambientes-con-balcon-y-baulera-54644316.html",
    "https://www.zonaprop.com.ar/propiedades/clasificado/veclapin-departamento-de-1-ambiente-en-caballito-fragata-54645341.html",
    "https://www.zonaprop.com.ar/propiedades/clasificado/veclapin-departamento-en-venta-en-nunez-capital-federal-54643952.html",
    "https://www.zonaprop.com.ar/propiedades/clasificado/veclapin-venta-departamento-consultorio-y-vivienda-4-ambientes-54644398.html",
    "https://www.zonaprop.com.ar/propiedades/clasificado/veclapin-venta-departamento-2-ambientes-con-toilette-balcon-al-54644379.html",
    "https://www.zonaprop.com.ar/propiedades/clasificado/veclapin-departamento-2-ambientes-al-frente-con-balcon.-venta-a-54643615.html",
    "https://www.zonaprop.com.ar/propiedades/clasificado/veclapin-2-ambientes-en-venta-balcon-apto-credito-54645956.html",
    "https://www.zonaprop.com.ar/propiedades/clasificado/veclapin-2-ambientes-apto-credito!-54645436.html",
    "https://www.zonaprop.com.ar/propiedades/clasificado/veclapin-venta-departamento-4-ambientes-con-dependencia-en-54644384.html",
    "https://www.zonaprop.com.ar/propiedades/clasificado/veclapin-venta-3-ambientes-villa-urquiza-con-cochera-54648085.html"
]

# Esperar antes de comenzar
time.sleep(3)

for url in urls:
    # Copiar la URL al portapapeles
    pyperclip.copy(url)
    
    # Esperar un poco antes de la siguiente acción
    time.sleep(0.5)

    # Simular Ctrl + L (enfocar la barra de direcciones)
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.5)

    # Simular Ctrl + V (pegar la URL)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.1)

    # Presionar Enter para ir a la URL
    pyautogui.press('enter')
    time.sleep(1.5)  # Esperar a que la página cargue

    # Realizar un desplazamiento de mouse aleatorio (scroll)
    scroll_amount = random.randint(-500, 500)  # Cambiar el rango según sea necesario
    pyautogui.scroll(scroll_amount)
    time.sleep(0.5)

    # Abrir la consola del navegador
    pyautogui.hotkey('ctrl', 'shift', 'j')
    time.sleep(1.5)
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.1)

    # Comando para extraer información de las tarjetas de propiedad
    command = """
// Seleccionar el elemento <p> dentro de la clase TooltipButton
const pElement = document.querySelector('.TooltipButton-sc-1qjqw89-1.ffHYMB p');

if (pElement) {
    // Obtener el contenido del <p>
    const pContent = pElement.textContent;

    // Crear un elemento de texto temporal
    const tempElement = document.createElement('textarea');
    tempElement.value = pContent;
    document.body.appendChild(tempElement);

    // Seleccionar y copiar el contenido al portapapeles
    tempElement.select();
    document.execCommand('copy');

    // Eliminar el elemento temporal
    document.body.removeChild(tempElement);

    // Mostrar mensaje en consola
    console.log('Contenido copiado al portapapeles:', pContent);
} else {
    console.log('No se encontró ningún elemento <p> dentro de la clase especificada.');
}

"""

    
    # Pegar el comando en la consola
    pyperclip.copy(command)
    time.sleep(0.1)

    # Simular Ctrl + V para pegar el comando
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.1)

    # Presionar Enter para ejecutar el comando
    pyautogui.press('enter')
    
    # Esperar un momento para que se ejecute el comando y se copien los datos
    time.sleep(0.5)

    # Obtener los datos del portapapeles y hacer print en Python
    datos_extraidos = pyperclip.paste()  # Leer el contenido del portapapeles
    print(f"Datos extraídos de {url}:\n{datos_extraidos}\n")  # Imprimir los datos

    pyautogui.hotkey('ctrl', 'shift', 'j')



# Finalizar el script
print("Todas las URLs han sido procesadas.")
