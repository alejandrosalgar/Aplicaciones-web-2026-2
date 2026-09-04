from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class ProductoBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    precio: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(ProductoBase):
    pass


class ProductoOut(ProductoBase):
    id: UUID

    model_config = {"from_attributes": True}
