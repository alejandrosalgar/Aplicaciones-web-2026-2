from uuid import UUID, uuid4

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.database.database import Base


class Empleado(Base):
    __tablename__ = "empleados"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    cargo: Mapped[str] = mapped_column(String(120), nullable=False)
    departamento: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True)