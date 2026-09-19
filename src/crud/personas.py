from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.entities.personas import Persona
from src.schemas.personas import PersonaCreate, PersonaUpdate


def listar(db: Session) -> list[Persona]:
    return list(db.scalars(select(Persona).order_by(Persona.nombre)))


def obtener_por_id(db: Session, persona_id: UUID) -> Persona | None:
    return db.get(Persona, persona_id)


def crear(db: Session, datos: PersonaCreate) -> Persona:
    persona = Persona(nombre=datos.nombre, programa=datos.programa)
    db.add(persona)
    db.commit()
    db.refresh(persona)
    return persona


def actualizar(db: Session, persona: Persona, datos: PersonaUpdate) -> Persona:
    persona.nombre = datos.nombre
    persona.programa = datos.programa
    db.commit()
    db.refresh(persona)
    return persona


def eliminar(db: Session, persona: Persona) -> None:
    db.delete(persona)
    db.commit()
