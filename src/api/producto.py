from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database.database import get_db
from src.schemas.producto import ProductoCreate, ProductoUpdate, ProductoOut
from src.crud import producto as crud

router = APIRouter(prefix="/productos", tags=["productos"])

@router.post("/", response_model=ProductoOut)
def crear(producto: ProductoCreate, db: Session = Depends(get_db)):
    return crud.crear_producto(db, producto)

@router.get("/", response_model=list[ProductoOut])
def listar(db: Session = Depends(get_db)):
    return crud.listar_productos(db)

@router.get("/{producto_id}", response_model=ProductoOut)
def obtener(producto_id: str, db: Session = Depends(get_db)):
    producto = crud.obtener_producto(db, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@router.put("/{producto_id}", response_model=ProductoOut)
def actualizar(producto_id: str, datos: ProductoUpdate, db: Session = Depends(get_db)):
    producto = crud.actualizar_producto(db, producto_id, datos)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@router.delete("/{producto_id}")
def eliminar(producto_id: str, db: Session = Depends(get_db)):
    producto = crud.eliminar_producto(db, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"mensaje": "Producto eliminado"}
