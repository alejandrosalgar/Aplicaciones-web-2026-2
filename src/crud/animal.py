from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.entities.animal import Animal


def listar(db: Session) -> list[Animal]:
    return list(db.scalars(select(Animal).order_by(Animal.nombre)))


def obtener_por_id(db: Session, animal_id: UUID) -> Animal | None:
    return db.get(Animal, animal_id)


def crear(db: Session, nombre: str, especie: str) -> Animal:
    animal = Animal(nombre=nombre, especie=especie)
    db.add(animal)
    db.commit()
    db.refresh(animal)
    return animal


def actualizar(db: Session, animal: Animal, nombre: str, especie) -> Animal:
    animal.nombre = nombre
    animal.especie = especie
    db.commit()
    db.refresh(animal)
    return animal


def eliminar(db: Session, animal: Animal) -> None:
    db.delete(animal)
    db.commit()
