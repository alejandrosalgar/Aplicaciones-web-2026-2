"""Inserta datos iniciales exclusivamente para la tabla productos."""

import os
from decimal import Decimal

from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from src.entities.producto import Producto

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

PRODUCTOS_SEMILLA = [
    {"nombre": "Producto demo Juan 1", "precio": Decimal("10000.00")},
    {"nombre": "Producto demo Juan 2", "precio": Decimal("25000.00")},
]


def main() -> None:
    insertados = 0
    db = SessionLocal()
    try:
        for datos in PRODUCTOS_SEMILLA:
            existe = db.scalar(
                select(Producto).where(Producto.nombre == datos["nombre"])
            )
            if existe is not None:
                print(f"Ya existe: {datos['nombre']}")
                continue

            db.add(Producto(**datos))
            insertados += 1
            print(f"Insertado: {datos['nombre']}")

        db.commit()
    finally:
        db.close()

    print(f"Seeder de Producto terminado. Filas nuevas: {insertados}")


if __name__ == "__main__":
    main()
