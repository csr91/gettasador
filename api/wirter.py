import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Definir el alcance
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Cargar las credenciales
creds = ServiceAccountCredentials.from_json_keyfile_name('auth.json', scope)

# Autenticar y abrir la hoja
client = gspread.authorize(creds)
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1BvM9UimqDWovad5jymR3sozps1axGL4tMM1qRKgtk3Y/edit#gid=0")

# Seleccionar la primera hoja (puedes cambiar el índice si tienes más de una hoja)
worksheet = sheet.get_worksheet(0)

# Escribir "hola" en la celda A2
worksheet.update_acell('A2', 'Hola')
