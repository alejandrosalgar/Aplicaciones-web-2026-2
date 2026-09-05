from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.crud import personas as repo
from src.database.database import get_db
from src.schemas.personas import PersonaCreate, PersonaRead, PersonaUpdate

router = APIRouter(prefix="/personas", tags=["personas"])


@router.get("", response_model=list[PersonaRead])
def listar_personas(db: Session = Depends(get_db)):
    return repo.listar(db)


@router.get("/{persona_id}", response_model=PersonaRead)
def obtener_persona(persona_id: UUID, db: Session = Depends(get_db)):
    persona = repo.obtener_por_id(db, persona_id)
    if persona is None:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return persona


@router.post(
    "",
    response_model=PersonaRead,
    status_code=status.HTTP_201_CREATED,
)
def crear_persona(datos: PersonaCreate, db: Session = Depends(get_db)):
    return repo.crear(db, datos)


@router.put("/{persona_id}", response_model=PersonaRead)
def actualizar_persona(
    persona_id: UUID,
    datos: PersonaUpdate,
    db: Session = Depends(get_db),
):
    persona = repo.obtener_por_id(db, persona_id)
    if persona is None:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return repo.actualizar(db, persona, datos)


@router.delete("/{persona_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_persona(persona_id: UUID, db: Session = Depends(get_db)):
    persona = repo.obtener_por_id(db, persona_id)
    if persona is None:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    repo.eliminar(db, persona)
