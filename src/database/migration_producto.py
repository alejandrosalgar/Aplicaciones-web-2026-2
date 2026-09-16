"""Crea exclusivamente la tabla productos si aun no existe."""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

from src.entities.producto import Producto

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def main() -> None:
    Producto.__table__.create(bind=engine, checkfirst=True)
    print("Tabla productos verificada/creada.")


if __name__ == "__main__":
    main()
