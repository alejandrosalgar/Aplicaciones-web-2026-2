from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.crud import animal as repo
from src.database.database import get_db
from src.entities.animal import Animal

router = APIRouter(prefix="/animales", tags=["animales"])


def _serializar(animal: Animal) -> dict:
    return {
        "id": str(animal.id),
        "nombre": animal.nombre,
        "especie": animal.especie,
    }


@router.get("")
def listar_animales(db: Session = Depends(get_db)):
    return [_serializar(a) for a in repo.listar(db)]


@router.get("/{animal_id}")
def obtener_animal(animal_id: UUID, db: Session = Depends(get_db)):
    animal = repo.obtener_por_id(db, animal_id)
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal no encontrado")
    return _serializar(animal)


@router.post("", status_code=status.HTTP_201_CREATED)
def crear_animal(
    nombre: str = Body(...),
    especie: str = Body(...),
    db: Session = Depends(get_db),
):
    animal = repo.crear(db, nombre, especie)
    return _serializar(animal)


@router.put("/{animal_id}")
def actualizar_animal(
    animal_id: UUID,
    nombre: str = Body(...),
    especie: str = Body(...),
    db: Session = Depends(get_db),
):
    animal = repo.obtener_por_id(db, animal_id)
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal no encontrado")
    return _serializar(repo.actualizar(db, animal, nombre, especie))


@router.delete("/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_animal(animal_id: UUID, db: Session = Depends(get_db)):
    animal = repo.obtener_por_id(db, animal_id)
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal no encontrado")
    repo.eliminar(db, animal)
