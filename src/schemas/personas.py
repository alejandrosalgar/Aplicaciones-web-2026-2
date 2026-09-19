from uuid import UUID

from pydantic import BaseModel


class PersonaRead(BaseModel):
    id: UUID
    nombre: str
    programa: str

    model_config = {"from_attributes": True}


class PersonaCreate(BaseModel):
    data: PersonaRead
    status: int
    message: str


class PersonaUpdate(BaseModel):
    data: PersonaRead
    status: int
    message: str


class PersonasGet(BaseModel):
    data: list[PersonaRead]
    status: int
    message: str


class PersonaGet(BaseModel):
    data: PersonaRead
    status: int
    message: str
    message: str
    message: str


class PersonaDelete(BaseModel):
    data: UUID
    status: int
    message: str
