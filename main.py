from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.animal import router as animal_router
from src.api.empleados import router as empleados_router
from src.api.personas import router as personas_router
from src.api.product import router as product_router
from src.api.producto import router as productos_router
from src.database.database import Base, engine
from src.entities.empleados import Empleado
from src.entities.personas import Persona

# Entidades
from src.entities.product import Product
from src.entities.producto import Producto

MODELOS = (Product, Producto, Empleado, Persona)


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def inicio():
    return {
        "mensaje": "API de ejemplo - Aplicaciones y servicios web ITM 2026-2",
        "docs": "/docs",
    }


# Routers
app.include_router(personas_router)
app.include_router(animal_router)
app.include_router(empleados_router)
app.include_router(product_router)
app.include_router(productos_router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.2", port=8000)
