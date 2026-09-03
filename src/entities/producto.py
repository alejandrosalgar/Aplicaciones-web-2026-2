from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID, uuid4
from src.database.database import Base

class Producto(Base):
    __tablename__ = "productos"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    nombre: Mapped[str] = mapped_column(String(120))
    precio: Mapped[str] = mapped_column(String(50))
