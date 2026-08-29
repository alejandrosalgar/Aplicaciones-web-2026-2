from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import String, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from src.database.database import Base


class Product(Base):
    __tablename__ = "products"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(25))
    sku: Mapped[str] = mapped_column(String(50),unique=True)
    cost: Mapped[Decimal] = mapped_column(Numeric(10,2))
    stock: Mapped[int] = mapped_column()
    available: Mapped[bool] = mapped_column()
    image_url: Mapped[str | None] = mapped_column(String(300),nullable=True)
    brand: Mapped[str] = mapped_column(String(50),nullable=True)








