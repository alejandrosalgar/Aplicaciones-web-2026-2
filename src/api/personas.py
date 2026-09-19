from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.crud import personas as repo
from src.database.database import get_db
from src.schemas.personas import PersonaCreate, PersonaGet, PersonasGet, PersonaUpdate

router = APIRouter(prefix="/personas", tags=["personas"])


@router.get("", response_model=list[PersonasGet])
def listar_personas(db: Session = Depends(get_db)) -> PersonasGet:
    personas = repo.listar(db)
    if personas is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND.value, detail="Personas no encontradas"
        )
    return (
        {
            "data": personas,
            "status": HTTPStatus.OK.value,
            "message": "Personas encontradas correctamente",
        },
    )


@router.get("/{persona_id}", response_model=PersonaGet)
def obtener_persona(persona_id: UUID, db: Session = Depends(get_db)) -> PersonaGet:
    persona = repo.obtener_por_id(db, persona_id)
    if persona is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND.value, detail="Persona no encontrada"
        )
    return {
        "data": persona,
        "status": HTTPStatus.OK.value,
        "message": "Persona encontrada correctamente",
    }


@router.post(
    "",
    response_model=PersonaCreate,
    status_code=status.HTTP_201_CREATED,
)
def crear_persona(datos: PersonaCreate, db: Session = Depends(get_db)):
    persona = repo.crear(db, datos)
    if persona is None:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            detail="Error al crear la persona",
        )
    return {
        "data": persona,
        "status": HTTPStatus.CREATED.value,
        "message": f"Persona creada con el nombre {persona.nombre} correctamente",
    }


@router.put("/{persona_id}", response_model=PersonaUpdate)
def actualizar_persona(
    persona_id: UUID,
    datos: PersonaUpdate,
    db: Session = Depends(get_db),
):
    persona = repo.obtener_por_id(db, persona_id)
    if persona is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND.value, detail="Persona no encontrada"
        )
    persona_actualizada = repo.actualizar(db, persona, datos)
    return {
        "data": persona_actualizada,
        "status": HTTPStatus.OK.value,
        "message": f"Persona actualizada con el nombre {persona_actualizada.nombre} correctamente",
    }


@router.delete("/{persona_id}", status_code=status.HTTP_200_OK)
def eliminar_persona(persona_id: UUID, db: Session = Depends(get_db)):
    persona = repo.obtener_por_id(db, persona_id)
    if persona is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND.value,
            detail="Persona no encontrada",
        )
    repo.eliminar(db, persona)
