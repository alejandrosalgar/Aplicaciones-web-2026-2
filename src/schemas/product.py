from uuid import UUID

from pydantic import BaseModel, Field
from decimal import Decimal



class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=1, max_length=200)
    category: str = Field(min_length=1, max_length=25)
    sku: str = Field(min_length=1, max_length=50)
    cost: Decimal = Field(gt=0)
    stock: int = Field(ge=0)
    available: bool = Field(default=True)
    image_url: str | None = Field(default=None, max_length=300)
    brand: str |None = Field(default=None, max_length=80)

class ProductUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=1, max_length=200)
    category: str = Field(min_length=1, max_length=25)
    sku: str = Field(min_length=1, max_length=50)
    cost: Decimal = Field(gt=0)
    stock: int = Field(ge=0)
    available: bool = Field(default=True)
    image_url: str | None = Field(default=None, max_length=300)
    brand: str | None = Field(default=None, max_length=80)


class ProductRead(BaseModel):
    id: UUID
    name: str
    description: str
    category: str
    sku: str
    cost: Decimal
    stock: int
    available: bool
    image_url: str | None
    brand: str | None

    model_config = {"from_attributes": True}
