from pydantic import BaseModel

class ProductoBase(BaseModel):
    nombre: str
    precio: str

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(ProductoBase):
    pass

class ProductoOut(ProductoBase):
    id: str

    class Config:
        orm_mode = True
