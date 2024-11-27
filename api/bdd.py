import mysql.connector

db_config = {
    'host': '172.245.184.156',
    'user': 'integracion',
    'password': 'lalita2024',
    'database': 'inmob',
    'port': 3306
}

# db_config = {
#     'host': 'localhost',
#     'user': 'root',
#     'password': 'inrepair9843',
#     'database': 'cannubis',
#     'port': 3306
# }

# Función para obtener una nueva conexión a la base de datos
def get_connection():
    return mysql.connector.connect(
        host="172.245.184.156",
        user="integracion",
        password="lalita2024",
        database="inmob"
    )