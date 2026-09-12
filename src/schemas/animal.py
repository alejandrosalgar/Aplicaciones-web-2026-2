from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AnimalCreate(BaseModel):
    nombre: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )
    especie: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )


class AnimalUpdate(BaseModel):
    nombre: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )
    especie: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )


class AnimalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nombre: str
    especie: str
