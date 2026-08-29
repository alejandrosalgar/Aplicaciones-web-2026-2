from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.crud import empleados as repo
from src.database.database import get_db
from src.schemas.empleados import EmpleadoCreate, EmpleadoRead, EmpleadoUpdate

router = APIRouter(prefix="/empleados", tags=["empleados"])


@router.get("", response_model=list[EmpleadoRead])
def listar_empleados(db: Session = Depends(get_db)):
    return repo.listar(db)


@router.get("/{empleado_id}", response_model=EmpleadoRead)
def obtener_empleado(empleado_id: UUID, db: Session = Depends(get_db)):
    empleado = repo.obtener_por_id(db, empleado_id)
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado


@router.post("", response_model=EmpleadoRead, status_code=status.HTTP_201_CREATED)
def crear_empleado(datos: EmpleadoCreate, db: Session = Depends(get_db)):
    return repo.crear(db, datos)


@router.put("/{empleado_id}", response_model=EmpleadoRead)
def actualizar_empleado(
    empleado_id: UUID,
    datos: EmpleadoUpdate,
    db: Session = Depends(get_db),
):
    empleado = repo.obtener_por_id(db, empleado_id)
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return repo.actualizar(db, empleado, datos)


@router.delete("/{empleado_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_empleado(empleado_id: UUID, db: Session = Depends(get_db)):
    empleado = repo.obtener_por_id(db, empleado_id)
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    repo.eliminar(db, empleado)