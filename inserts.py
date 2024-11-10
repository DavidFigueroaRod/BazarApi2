import json
import pymysql
import os
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

# Conectar a la base de datos
db = pymysql.connect(
    host="b81vvkettllvuvrvwsao-mysql.services.clever-cloud.com",
    user="ulcscuyqojukvozt",
    password="SWKtbm1Puqkdf8zD17AB",
    database="b81vvkettllvuvrvwsao",
    port=3306
)

cursor = db.cursor()

# Leer el archivo JSON
with open('products.json') as f:
    products = json.load(f)

# Función para convertir fechas al formato adecuado
def convert_datetime(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# Insertar cada producto en la tabla
for product in products['products']:
    sql = """
        INSERT INTO productos_completos (
            id, title, description, category, price, discountPercentage, rating, stock, tags, brand, sku, weight, 
            dimensions_width, dimensions_height, dimensions_depth, warrantyInformation, shippingInformation, 
            availabilityStatus, reviews, returnPolicy, minimumOrderQuantity, createdAt, updatedAt, barcode, qrCode, 
            images, thumbnail
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    """
    cursor.execute(sql, (
        product['id'],
        product.get('title', ''),
        product.get('description', ''),
        product.get('category', ''),
        product.get('price', 0.0),
        product.get('discountPercentage', 0.0),
        product.get('rating', 0.0),
        product.get('stock', 0),
        json.dumps(product.get('tags', [])),
        product.get('brand', ''),
        product.get('sku', ''),
        product.get('weight', 0),
        product.get('dimensions', {}).get('width', 0.0),
        product.get('dimensions', {}).get('height', 0.0),
        product.get('dimensions', {}).get('depth', 0.0),
        product.get('warrantyInformation', ''),
        product.get('shippingInformation', ''),
        product.get('availabilityStatus', ''),
        json.dumps(product.get('reviews', [])),
        product.get('returnPolicy', ''),
        product.get('minimumOrderQuantity', 0),
        convert_datetime(product['meta']['createdAt']),
        convert_datetime(product['meta']['updatedAt']),
        product['meta'].get('barcode', ''),
        product['meta'].get('qrCode', ''),
        json.dumps(product.get('images', [])),
        product.get('thumbnail', '')
    ))

# Confirmar cambios y cerrar la conexión
db.commit()
cursor.close()
db.close()

print("Datos insertados con éxito.")
