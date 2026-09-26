import os
import unittest
from unittest.mock import patch
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "sqlite://")

from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from src.api import empleados as empleado_api  # noqa: E402
from src.database.database import get_db  # noqa: E402


app = FastAPI()
app.include_router(empleado_api.router)
app.dependency_overrides[get_db] = lambda: object()


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
