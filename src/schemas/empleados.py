from uuid import UUID

from pydantic import BaseModel, Field


class EmpleadoCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    cargo: str = Field(min_length=1, max_length=120)
    departamento: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=3, max_length=254)


class EmpleadoUpdate(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    cargo: str = Field(min_length=1, max_length=120)
    departamento: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=3, max_length=254)


class EmpleadoRead(BaseModel):
    id: UUID
    nombre: str
    cargo: str
    departamento: str
    email: str

    model_config = {"from_attributes": True}
