"""Datos iniciales de la base. Se puede ejecutar cuantas veces se quiera."""

# pylint: disable=duplicate-code

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.database import Base, SessionLocal, engine
from src.entities.animal import Animal

ANIMALES_SEMILLA = [
    {"nombre": "Rex", "especie": "Perro"},
    {"nombre": "Oliver", "especie": "Gato"},
]


def crear_tablas() -> None:
    """Crea las tablas que aun no existen. No modifica las que ya estan."""
    Base.metadata.create_all(bind=engine)


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
        animales = _insertar_si_falta(db, Animal, "nombre", ANIMALES_SEMILLA)
    finally:
        db.close()

    print(f"Seeder terminado. Filas nuevas: {animales}")


if __name__ == "__main__":
    main()
