import os
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "sqlite://")

import pytest  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.exc import SQLAlchemyError  # noqa: E402

from src.api import empleados as empleado_api  # noqa: E402
from src.database.database import get_db  # noqa: E402


app = FastAPI()
app.include_router(empleado_api.router)
app.dependency_overrides[get_db] = lambda: object()

DATOS_VALIDOS = {
    "nombre": "Ana",
    "cargo": "Analista",
    "departamento": "TI",
    "email": "ana@example.com",
}


def crear_empleado():
    return {"id": str(uuid4()), **DATOS_VALIDOS}


@pytest.fixture
def db_session():
    return MagicMock()


@pytest.fixture
def client(db_session):
    app_pruebas = FastAPI()
    app_pruebas.include_router(empleado_api.router)
    app_pruebas.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app_pruebas) as test_client:
        yield test_client
    app_pruebas.dependency_overrides.clear()


def test_listar_empleados_devuelve_lista(client, monkeypatch):
    empleados = [crear_empleado()]
    monkeypatch.setattr(empleado_api.repo, "listar", lambda _db: empleados)

    response = client.get("/empleados")

    assert response.status_code == 200
    assert response.json() == empleados


def test_listar_empleados_devuelve_503_si_falla_la_base(
    client, monkeypatch, db_session
):
    def fallar(_db):
        raise SQLAlchemyError("detalle interno")

    monkeypatch.setattr(empleado_api.repo, "listar", fallar)

    response = client.get("/empleados")

    assert response.status_code == 503
    assert response.json() == {"detail": "Base de datos no disponible"}
    db_session.rollback.assert_called_once()


def test_obtener_empleado_devuelve_registro(client, monkeypatch):
    empleado = crear_empleado()
    monkeypatch.setattr(
        empleado_api.repo, "obtener_por_id", lambda _db, _id: empleado
    )

    response = client.get(f"/empleados/{empleado['id']}")

    assert response.status_code == 200
    assert response.json() == empleado


def test_obtener_empleado_inexistente_devuelve_404(client, monkeypatch):
    monkeypatch.setattr(
        empleado_api.repo, "obtener_por_id", lambda _db, _id: None
    )

    response = client.get(f"/empleados/{uuid4()}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Empleado no encontrado"}


def test_crear_empleado_devuelve_201(client, monkeypatch):
    empleado = crear_empleado()
    monkeypatch.setattr(
        empleado_api.repo, "crear", lambda _db, _datos: empleado
    )

    response = client.post("/empleados", json=DATOS_VALIDOS)

    assert response.status_code == 201
    assert response.json() == empleado


def test_crear_empleado_rechaza_email_invalido(client):
    datos = {**DATOS_VALIDOS, "email": "correo-invalido"}

    response = client.post("/empleados", json=datos)

    assert response.status_code == 422
    assert any(
        error["loc"][-1] == "email" for error in response.json()["detail"]
    )


def test_actualizar_empleado_devuelve_registro_actualizado(
    client, monkeypatch
):
    empleado = crear_empleado()
    actualizado = {**empleado, "cargo": "Lider tecnica"}
    monkeypatch.setattr(
        empleado_api.repo, "obtener_por_id", lambda _db, _id: empleado
    )
    monkeypatch.setattr(
        empleado_api.repo,
        "actualizar",
        lambda _db, _empleado, _datos: actualizado,
    )

    response = client.put(
        f"/empleados/{empleado['id']}",
        json={**DATOS_VALIDOS, "cargo": "Lider tecnica"},
    )

    assert response.status_code == 200
    assert response.json() == actualizado


def test_actualizar_empleado_inexistente_devuelve_404(client, monkeypatch):
    monkeypatch.setattr(
        empleado_api.repo, "obtener_por_id", lambda _db, _id: None
    )

    response = client.put(f"/empleados/{uuid4()}", json=DATOS_VALIDOS)

    assert response.status_code == 404
    assert response.json() == {"detail": "Empleado no encontrado"}


def test_eliminar_empleado_devuelve_204(client, monkeypatch):
    empleado = crear_empleado()
    monkeypatch.setattr(
        empleado_api.repo, "obtener_por_id", lambda _db, _id: empleado
    )
    monkeypatch.setattr(
        empleado_api.repo, "eliminar", lambda _db, _empleado: None
    )

    response = client.delete(f"/empleados/{empleado['id']}")

    assert response.status_code == 204
    assert response.content == b""


def test_eliminar_empleado_inexistente_devuelve_404(client, monkeypatch):
    monkeypatch.setattr(
        empleado_api.repo, "obtener_por_id", lambda _db, _id: None
    )

    response = client.delete(f"/empleados/{uuid4()}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Empleado no encontrado"}


class EmpleadosApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()

    def test_crear_empleado_con_email_valido(self):
        empleado_id = uuid4()
        empleado = {
            "id": str(empleado_id),
            "nombre": "Ana",
            "cargo": "Analista",
            "departamento": "TI",
            "email": "ana@example.com",
        }
        with patch.object(empleado_api.repo, "crear", return_value=empleado):
            response = self.client.post("/empleados", json=empleado)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), empleado)

    def test_crear_empleado_rechaza_datos_invalidos(self):
        response = self.client.post(
            "/empleados",
            json={
                "nombre": "",
                "cargo": "Analista",
                "departamento": "TI",
                "email": "esto-no-es-un-correo",
            },
        )

        self.assertEqual(response.status_code, 422)
        invalid_fields = {
            error["loc"][-1] for error in response.json()["detail"]
        }
        self.assertIn("nombre", invalid_fields)
        self.assertIn("email", invalid_fields)

    def test_actualizar_empleado_rechaza_email_invalido(self):
        response = self.client.put(
            f"/empleados/{uuid4()}",
            json={
                "nombre": "Ana",
                "cargo": "Analista",
                "departamento": "TI",
                "email": "correo-invalido",
            },
        )

        self.assertEqual(response.status_code, 422)

    def test_operaciones_sobre_empleado_inexistente_devuelven_404(self):
        empleado_id = uuid4()
        datos = {
            "nombre": "Ana",
            "cargo": "Analista",
            "departamento": "TI",
            "email": "ana@example.com",
        }
        with patch.object(
            empleado_api.repo, "obtener_por_id", return_value=None
        ):
            respuestas = (
                self.client.get(f"/empleados/{empleado_id}"),
                self.client.put(f"/empleados/{empleado_id}", json=datos),
                self.client.delete(f"/empleados/{empleado_id}"),
            )

        self.assertEqual(
            [respuesta.status_code for respuesta in respuestas], [404] * 3
        )
        self.assertEqual(
            [respuesta.json()["detail"] for respuesta in respuestas],
            ["Empleado no encontrado"] * 3,
        )


if __name__ == "__main__":
    unittest.main()
