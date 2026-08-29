from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.crud import product as repo
from src.database.database import get_db
from src.schemas.product import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(prefix="/products", tags=["producto"])


@router.get("", response_model=list[ProductRead])
def list_product(db: Session = Depends(get_db)):
    return repo.list_product(db)


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    product = repo.get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.post(
    "",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    return repo.create_product(db, data)


@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: UUID, data: ProductUpdate, db: Session = Depends(get_db)
):
    product = repo.get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return repo.update_product(db, product, data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: UUID, db: Session = Depends(get_db)):
    product = repo.get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    repo.delete_product(db, product)
