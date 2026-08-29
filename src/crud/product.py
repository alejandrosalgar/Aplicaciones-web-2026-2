from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.entities.product import Product
from src.schemas.product import ProductCreate, ProductUpdate


def list_product(db: Session) -> list[Product]:
    return list(db.scalars(select(Product).order_by(Product.name)))


def get_product_by_id(db: Session, product_id: UUID) -> Product | None:
    return db.get(Product, product_id)


def create_product(db: Session, data: ProductCreate) -> Product:
    product = Product(
        name=data.name,
        description=data.description,
        category=data.category,
        sku=data.sku,
        cost=data.cost,
        stock=data.stock,
        available=data.available,
        image_url=data.image_url,
        brand=data.brand,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(
    db: Session, product: Product, data: ProductUpdate
) -> Product:
    product.name = data.name
    product.description = data.description
    product.category = data.category
    product.sku = data.sku
    product.cost = data.cost
    product.stock = data.stock
    product.available = data.available
    product.image_url = data.image_url
    product.brand = data.brand
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: Product) -> None:
    db.delete(product)
    db.commit()
