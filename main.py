from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import mysql.connector
from mysql.connector import Error
import uvicorn
from datetime import datetime
# from datetime import date

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
class Product(BaseModel):
    id: int
    title: str
    description: str
    price: float
    discountPercentage: float
    rating: float
    stock: int
    brand: str
    category: str
    thumbnail: str
    images: str
    tags: Optional[str] = None
    sku: Optional[str] = None
    weight: Optional[int] = None
    dimensions_width: Optional[float] = None
    dimensions_height: Optional[float] = None
    dimensions_depth: Optional[float] = None
    warrantyInformation: Optional[str] = None
    shippingInformation: Optional[str] = None
    availabilityStatus: Optional[str] = None
    returnPolicy: Optional[str] = None
    minimumOrderQuantity: Optional[int] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    barcode: Optional[str] = None
    qrCode: Optional[str] = None

# Modelo para representar una venta con detalles del producto
class SaleWithProduct(BaseModel):
    id: int
    product_id: int
    price: float
    sale_date: datetime  # Cambiado a datetime para incluir la hora si es necesario
    product: Product

# Modelo para agregar una venta
class SaleInput(BaseModel):
    product_id: int
    price: float
    sale_date: datetime

# Endpoint para obtener todos los productos
@app.get("/products/", response_model=List[Product])
def get_products():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos_completos")
        products = cursor.fetchall()
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
    query = """
        SELECT * FROM productos_completos 
        WHERE title LIKE %s OR description LIKE %s OR category LIKE %s
    """
    cursor.execute(query, (f"%{q}%", f"%{q}%", f"%{q}%"))
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
    cursor.execute("SELECT * FROM productos_completos WHERE id = %s", (item_id,))
    item = cursor.fetchone()
    conn.close()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# Endpoint para registrar una venta
from datetime import datetime

from datetime import datetime
from fastapi import HTTPException


from fastapi import HTTPException

@app.post("/api/addSale")
def add_sale(sale: SaleInput):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        # Usa sale.sale_date directamente, sin conversión adicional
        cursor.execute("INSERT INTO ventas (producto_id, precio, fecha_venta) VALUES (%s, %s, %s)",
                       (sale.product_id, sale.price, sale.sale_date))
        conn.commit()
        result = True
    except mysql.connector.Error as e:
        conn.rollback()
        print(f"Error al insertar en la base de datos: {e}")
        result = False
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {e}")
    finally:
        cursor.close()
        conn.close()
    return {"success": result}



# Endpoint para obtener todas las ventas con detalles del producto
@app.get("/api/sales", response_model=List[SaleWithProduct])
def get_sales():
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Consulta SQL que incluye los datos del producto usando JOIN
        query = """
        SELECT ventas.id, ventas.producto_id, ventas.precio, ventas.fecha_venta,
               productos_completos.id AS product_id, productos_completos.title, productos_completos.description, 
               productos_completos.price AS product_price, productos_completos.discountPercentage, productos_completos.rating,
               productos_completos.stock, productos_completos.brand, productos_completos.category, productos_completos.thumbnail, productos_completos.images
        FROM ventas
        JOIN productos_completos ON ventas.producto_id = productos_completos.id
        """

        cursor.execute(query)
        sales = cursor.fetchall()

        # Cerrar la conexión
        cursor.close()
        connection.close()

        # Transformar los resultados para ajustarse al modelo de respuesta
        sales_with_product = [
            {
                "id": sale["id"],
                "product_id": sale["producto_id"],
                "price": sale["precio"],
                "sale_date": sale["fecha_venta"],
                "product": {
                    "id": sale["product_id"],
                    "title": sale["title"],
                    "description": sale["description"],
                    "price": sale["product_price"],
                    "discountPercentage": sale["discountPercentage"],
                    "rating": sale["rating"],
                    "stock": sale["stock"],
                    "brand": sale["brand"],
                    "category": sale["category"],
                    "thumbnail": sale["thumbnail"],
                    "images": sale["images"]
                }
            } for sale in sales
        ]

        if not sales_with_product:
            raise HTTPException(status_code=404, detail="No sales found")

        return sales_with_product

    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar la base de datos: {e}")



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
