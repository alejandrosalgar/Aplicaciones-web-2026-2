from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.crud import animal as repo
from src.database.database import get_db
from src.schemas.animal import AnimalCreate, AnimalRead, AnimalUpdate

router = APIRouter(prefix="/animales", tags=["animales"])


@router.get(
    "",
    response_model=list[AnimalRead],
    status_code=status.HTTP_200_OK,
)
def listar_animales(db: Session = Depends(get_db)):
    return repo.listar(db)


@router.get(
    "/{animal_id}",
    response_model=AnimalRead,
    status_code=status.HTTP_200_OK,
)
def obtener_animal(animal_id: UUID, db: Session = Depends(get_db)):
    animal = repo.obtener_por_id(db, animal_id)
    if animal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No encontrado"
        )
    return animal


@router.post(
    "",
    response_model=AnimalRead,
    status_code=status.HTTP_201_CREATED,
)
def crear_animal(datos: AnimalCreate, db: Session = Depends(get_db)):
    try:
        return repo.crear(db, datos)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Datos invalidos para la creacion del animal",
        ) from exc


@router.put(
    "/{animal_id}",
    response_model=AnimalRead,
    status_code=status.HTTP_200_OK,
)
def actualizar_animal(
    animal_id: UUID,
    datos: AnimalUpdate,
    db: Session = Depends(get_db),
):
    animal = repo.obtener_por_id(db, animal_id)
    if animal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No encontrado"
        )
    try:
        return repo.actualizar(db, animal, datos)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Datos invalidos para la actualizacion del animal",
        ) from exc


@router.delete("/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_animal(animal_id: UUID, db: Session = Depends(get_db)):
    animal = repo.obtener_por_id(db, animal_id)
    if animal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No encontrado"
        )
    repo.eliminar(db, animal)
