"""Datos iniciales de la base. Se puede ejecutar cuantas veces se quiera."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.database import Base, SessionLocal, engine
from src.entities import Empleado, Persona, Product

PERSONAS_SEMILLA = [
    {"nombre": "Ana Perez", "programa": "Ingenieria de Sistemas"},
    {"nombre": "Carlos Ramirez", "programa": "Ingenieria de Software"},
    {"nombre": "Laura Gomez", "programa": "Ingenieria Electronica"},
]

EMPLEADOS_SEMILLA = [
    {
        "nombre": "Ana Perez",
        "cargo": "Docente",
        "departamento": "Sistemas",
        "email": "ana.perez@itm.edu.co",
    },
    {
        "nombre": "Carlos Ramirez",
        "cargo": "Coordinador",
        "departamento": "Software",
        "email": "carlos.ramirez@itm.edu.co",
    },
    {
        "nombre": "Laura Gomez",
        "cargo": "Docente",
        "departamento": "Electronica",
        "email": "laura.gomez@itm.edu.co",
    },
]

PRODUCTOS_SEMILLA = [
    {
        "name": "Teclado mecanico",
        "description": "Teclado para laboratorio de desarrollo",
        "category": "Perifericos",
        "sku": "TEC-001",
        "cost": Decimal("120000.00"),
        "stock": 15,
        "available": True,
        "image_url": None,
        "brand": "Keychron",
    },
    {
        "name": "Mouse inalambrico",
        "description": "Mouse inalambrico para salas de computo",
        "category": "Perifericos",
        "sku": "MOU-001",
        "cost": Decimal("45000.00"),
        "stock": 30,
        "available": True,
        "image_url": None,
        "brand": "Logitech",
    },
    {
        "name": "Monitor 24 pulgadas",
        "description": "Monitor Full HD para puestos de trabajo",
        "category": "Pantallas",
        "sku": "MON-001",
        "cost": Decimal("650000.00"),
        "stock": 8,
        "available": True,
        "image_url": None,
        "brand": "Dell",
    },
]


def crear_tablas() -> None:
    """Crea las tablas que aun no existen. No modifica las que ya estan."""
    Base.metadata.create_all(bind=engine)
    print("Tablas verificadas/creadas.")


def _insertar_si_falta(
    db: Session,
    modelo: type,
    campo: str,
    filas: list[dict],
) -> int:
    insertadas = 0
    columna = getattr(modelo, campo)

    for datos in filas:
        etiqueta = datos[campo]
        existe = db.scalar(select(modelo).where(columna == etiqueta))
        if existe is not None:
            print(f"Ya existe: {etiqueta}")
            continue

        db.add(modelo(**datos))
        insertadas += 1
        print(f"Insertada: {etiqueta}")

    db.commit()
    return insertadas


def main() -> None:
    crear_tablas()

    db = SessionLocal()
    try:
        personas = _insertar_si_falta(db, Persona, "nombre", PERSONAS_SEMILLA)
        empleados = _insertar_si_falta(
            db, Empleado, "email", EMPLEADOS_SEMILLA
        )
        productos = _insertar_si_falta(db, Product, "sku", PRODUCTOS_SEMILLA)
    finally:
        db.close()

    total = personas + empleados + productos
    print(f"Seeder terminado. Filas nuevas: {total}")


if __name__ == "__main__":
    main()
