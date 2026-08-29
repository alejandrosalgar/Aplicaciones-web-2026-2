from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.entities.animal import Animal
from src.schemas.animal import AnimalCreate, AnimalUpdate


def listar(db: Session) -> list[Animal]:
    return list(db.scalars(select(Animal).order_by(Animal.nombre)))


def obtener_por_id(db: Session, animal_id: UUID) -> Animal | None:
    return db.get(Animal, animal_id)


def existe_nombre(db: Session, nombre, excluir_id: UUID | None = None):
    stmt = select(Animal).where(Animal.nombre == nombre)
    if excluir_id is not None:
        stmt = stmt.where(Animal.id != excluir_id)
    return db.scalars(stmt).first() is not None


def crear(db: Session, datos: AnimalCreate) -> Animal:
    if existe_nombre(db, datos.nombre):
        raise ValueError(f"Ya existe un animal con el nombre '{datos.nombre}'")

    animal = Animal(nombre=datos.nombre, especie=datos.especie)
    db.add(animal)
    db.commit()
    db.refresh(animal)
    return animal


def actualizar(db: Session, animal: Animal, datos: AnimalUpdate) -> Animal:
    if existe_nombre(db, datos.nombre, excluir_id=animal.id):
        raise ValueError(f"Ya existe un animal con el nombre '{datos.nombre}'")

    animal.nombre = datos.nombre
    animal.especie = datos.especie
    db.commit()
    db.refresh(animal)
    return animal


def eliminar(db: Session, animal: Animal) -> None:
    db.delete(animal)
    db.commit()
