import json
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

db = pymysql.connect(
    host=os.getenv("MYSQL_ADDON_HOST"),
    user=os.getenv("MYSQL_ADDON_USER"),
    password=os.getenv("MYSQL_ADDON_PASSWORD"),
    database=os.getenv("MYSQL_ADDON_DB"),
    port=int(os.getenv("MYSQL_ADDON_PORT"))
)

cursor = db.cursor()

with open('products.json') as f:
    products = json.load(f)

for product in products['products']:
    sql = """
        INSERT INTO products (id, title, description, price, discountPercentage, rating, stock, brand, category, thumbnail, images)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        product['id'],
        product['title'],
        product['description'],
        product['price'],
        product['discountPercentage'],
        product['rating'],
        product['stock'],
        product['brand'],
        product['category'],
        product['thumbnail'],
        json.dumps(product['images'])
    ))

db.commit()
cursor.close()
db.close()

print("Datos insertados con éxito.")
