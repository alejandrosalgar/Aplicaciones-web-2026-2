from uuid import UUID

from pydantic import BaseModel, Field


class PersonaCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    programa: str = Field(min_length=1, max_length=120)


class PersonaUpdate(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    programa: str = Field(min_length=1, max_length=120)


class PersonaRead(BaseModel):
    id: UUID
    nombre: str
    programa: str

    model_config = {"from_attributes": True}
