from http import HTTPStatus
from uuid import uuid4, UUID
from typing import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from src.database.database import Base, get_db
from src.entities.animal import Animal
from src.crud import animal as animal_crud

from main import app


@pytest.fixture(scope="function")
def engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    from sqlalchemy.dialects import sqlite
    import sqlalchemy.types as types

    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db(engine):
    with Session(engine) as session:
        yield session
        session.rollback()


@pytest.fixture
def client(db: Session) -> Iterator[TestClient]:
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def animal_base(db: Session) -> Animal:
    animal_base = Animal(nombre="Perro", especie="Canis lupus familiaris")
    return animal_crud.crear(db, animal_base)


def test_listar_animales(client: TestClient, animal_base: Animal):
    respuesta = client.get("/animales")
    assert respuesta.status_code == HTTPStatus.OK.value
    assert len(respuesta.json()) == 1


def test_listar_animales_vacio(client: TestClient):
    respuesta = client.get("/animales")
    assert respuesta.status_code == HTTPStatus.OK.value
    assert len(respuesta.json()) == 0


def test_obtener_animal(client: TestClient, animal_base: Animal):
    respuesta = client.get(f"/animales/{animal_base.id}")
    assert respuesta.status_code == HTTPStatus.OK.value
    assert respuesta.json()["id"] == str(animal_base.id)
    assert respuesta.json()["nombre"] == "Perro"
    assert respuesta.json()["especie"] == "Canis lupus familiaris"


def test_obtener_animal_inexistente(client: TestClient):
    respuesta = client.get(f"/animales/{uuid4()}")
    assert respuesta.status_code == HTTPStatus.NOT_FOUND.value
    assert respuesta.json()["detail"] == "No encontrado"


def test_crear_animal(client: TestClient):
    datos = {"nombre": "Gato", "especie": "Felis catus"}
    respuesta = client.post("/animales", json=datos)
    assert respuesta.status_code == HTTPStatus.CREATED.value
    assert respuesta.json()["nombre"] == "Gato"
    assert respuesta.json()["especie"] == "Felis catus"


def test_crear_animal_invalido(client: TestClient):
    datos = {"nombre": "Gato"}
    respuesta = client.post("/animales", json=datos)
    assert respuesta.status_code == HTTPStatus.UNPROCESSABLE_ENTITY.value


def test_actualizar_animal(client: TestClient, animal_base: Animal):
    datos = {"nombre": "Perro modificado", "especie": "Canis lupus familiaris"}
    respuesta = client.put(f"/animales/{animal_base.id}", json=datos)
    assert respuesta.status_code == HTTPStatus.OK.value
    assert respuesta.json()["nombre"] == "Perro modificado"


def test_actualizar_animal_inexistente(client: TestClient):
    datos = {"nombre": "Perro modificado", "especie": "Canis lupus familiaris"}
    respuesta = client.put(f"/animales/{uuid4()}", json=datos)
    assert respuesta.status_code == HTTPStatus.NOT_FOUND.value
    assert respuesta.json()["detail"] == "No encontrado"


def test_eliminar_animal(client: TestClient, animal_base: Animal):
    respuesta = client.delete(f"/animales/{animal_base.id}")
    assert respuesta.status_code == HTTPStatus.NO_CONTENT.value

    respuesta_get = client.get(f"/animales/{animal_base.id}")
    assert respuesta_get.status_code == HTTPStatus.NOT_FOUND.value
    assert respuesta_get.json()["detail"] == "No encontrado"


def test_eliminar_animal_inexistente(client: TestClient):
    respuesta = client.delete(f"/animales/{uuid4()}")
    assert respuesta.status_code == HTTPStatus.NOT_FOUND.value
    assert respuesta.json()["detail"] == "No encontrado"
