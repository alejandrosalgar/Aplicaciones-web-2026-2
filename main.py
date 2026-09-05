from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.empleados import router as empleados_router
from src.api.personas import router as personas_router
from src.api.product import router as product_router
from src.database.database import Base, engine


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="API Personas - ITM 2026-2",
    description="API REST con FastAPI, SQLAlchemy y Neon PostgreSQL",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def inicio():
    return {
        "mensaje": "API de ejemplo - Aplicaciones y servicios web ITM 2026-2",
        "docs": "/docs",
    }


app.include_router(personas_router)
app.include_router(empleados_router)
app.include_router(product_router)
