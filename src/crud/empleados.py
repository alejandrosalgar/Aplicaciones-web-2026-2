from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.entities.empleados import Empleado
from src.schemas.empleados import EmpleadoCreate, EmpleadoUpdate


def listar(db: Session) -> list[Empleado]:
    return list(db.scalars(select(Empleado).order_by(Empleado.nombre)))


def obtener_por_id(db: Session, empleado_id: UUID) -> Empleado | None:
    return db.get(Empleado, empleado_id)


def crear(db: Session, datos: EmpleadoCreate) -> Empleado:
    empleado = Empleado(
        nombre=datos.nombre,
        cargo=datos.cargo,
        departamento=datos.departamento,
        email=datos.email,
    )
    db.add(empleado)
    db.commit()
    db.refresh(empleado)
    return empleado


def actualizar(
    db: Session, empleado: Empleado, datos: EmpleadoUpdate
) -> Empleado:
    empleado.nombre = datos.nombre
    empleado.cargo = datos.cargo
    empleado.departamento = datos.departamento
    empleado.email = datos.email
    db.commit()
    db.refresh(empleado)
    return empleado


def eliminar(db: Session, empleado: Empleado) -> None:
    db.delete(empleado)
    db.commit()
