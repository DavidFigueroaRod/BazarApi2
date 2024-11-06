from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import mysql.connector
from mysql.connector import Error
import uvicorn
from datetime import date

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de conexión a MySQL
db_config = {
    "user": "ulcscuyqojukvozt",
    "password": "SWKtbm1Puqkdf8zD17AB",
    "host": "b81vvkettllvuvrvwsao-mysql.services.clever-cloud.com",
    "database": "b81vvkettllvuvrvwsao"
}

# Modelo para representar un producto
# Modelo para representar un producto
class Product(BaseModel):
    id: int
    title: str
    description: str
    price: float
    discountPercentage: float  # Cambiar el nombre aquí
    rating: float
    stock: int
    brand: str
    category: str
    thumbnail: str
    images: str  # Cambiar el nombre aquí

# Modelo para agregar una venta
class SaleInput(BaseModel):
    product_id: int
    price: float
    sale_date: date

# Endpoint para obtener todos los productos
@app.get("/products/", response_model=List[Product])
def get_products():
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Ejecutar la consulta SQL
        cursor.execute("SELECT * FROM productos")
        products = cursor.fetchall()

        # Cerrar la conexión
        cursor.close()
        connection.close()

        return products

    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar la base de datos: {e}")


# Endpoint para buscar productos
@app.get("/api/items", response_model=List[Product])
def get_items(q: Optional[str] = Query(None)):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM productos WHERE title LIKE %s OR description LIKE %s"
    cursor.execute(query, (f"%{q}%", f"%{q}%"))
    items = cursor.fetchall()
    conn.close()
    if not items:
        raise HTTPException(status_code=404, detail="No items found")
    return items

# Endpoint para obtener un producto por ID
@app.get("/api/items/{item_id}", response_model=Product)
def get_item(item_id: int):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos WHERE id = %s", (item_id,))
    item = cursor.fetchone()
    conn.close()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# Endpoint para registrar una venta
@app.post("/api/addSale")
def add_sale(sale: SaleInput):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO ventas (producto_id, precio, fecha_venta) VALUES (%s, %s, %s)",
                       (sale.product_id, sale.price, sale.sale_date))
        conn.commit()
        result = True
    except:
        conn.rollback()
        result = False
    finally:
        conn.close()
    return {"success": result}

# Endpoint para obtener todas las ventas
@app.get("/api/sales")
def get_sales():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ventas")
    sales = cursor.fetchall()
    conn.close()
    if not sales:
        raise HTTPException(status_code=404, detail="No sales found")
    return sales

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)