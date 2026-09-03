from sqlalchemy.orm import Session
from src.entities.producto import Producto
from src.schemas.producto import ProductoCreate, ProductoUpdate

def crear_producto(db: Session, producto: ProductoCreate):
    nuevo = Producto(nombre=producto.nombre, precio=producto.precio)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

def listar_productos(db: Session):
    return db.query(Producto).all()

def obtener_producto(db: Session, producto_id: str):
    return db.query(Producto).filter(Producto.id == producto_id).first()

def actualizar_producto(db: Session, producto_id: str, datos: ProductoUpdate):
    producto = obtener_producto(db, producto_id)
    if producto:
        producto.nombre = datos.nombre
        producto.precio = datos.precio
        db.commit()
        db.refresh(producto)
    return producto

def eliminar_producto(db: Session, producto_id: str):
    producto = obtener_producto(db, producto_id)
    if producto:
        db.delete(producto)
        db.commit()
    return producto
