from http import HTTPStatus
from uuid import uuid4

PERSONA_VALIDA = {
    "nombre": "Ana Perez",
    "programa": "Ingenieria de Sistemas",
}

PERSONA_ACTUALIZADA = {
    "nombre": "Ana Gomez",
    "programa": "Ingenieria de Software",
}


def _crear_persona(cliente, datos=None):
    respuesta = cliente.post("/personas", json=datos or PERSONA_VALIDA)
    assert respuesta.status_code == HTTPStatus.CREATED.value
    return respuesta.json()


def test_listar_personas_devuelve_200_y_una_lista(cliente):
    _crear_persona(cliente)
    respuesta = cliente.get("/personas")

    assert respuesta.status_code == HTTPStatus.OK.value
    cuerpo = respuesta.json()
    assert isinstance(cuerpo, list)
    assert len(cuerpo) == 1
    assert cuerpo[0]["nombre"] == PERSONA_VALIDA["nombre"]


def test_listar_personas_vacio_devuelve_200_y_lista_vacia(cliente):
    respuesta = cliente.get("/personas")

    assert respuesta.status_code == HTTPStatus.OK.value
    assert respuesta.json() == []


def test_obtener_persona_devuelve_200(cliente):
    creada = _crear_persona(cliente)
    respuesta = cliente.get(f"/personas/{creada['id']}")

    assert respuesta.status_code == HTTPStatus.OK.value
    cuerpo = respuesta.json()
    assert cuerpo["id"] == creada["id"]
    assert cuerpo["nombre"] == PERSONA_VALIDA["nombre"]
    assert cuerpo["programa"] == PERSONA_VALIDA["programa"]


def test_obtener_persona_inexistente_devuelve_404(cliente):
    respuesta = cliente.get(f"/personas/{uuid4()}")

    assert respuesta.status_code == HTTPStatus.NOT_FOUND.value
    assert respuesta.json()["detail"] == "Persona no encontrada"


def test_crear_persona_devuelve_201(cliente):
    respuesta = cliente.post("/personas", json=PERSONA_VALIDA)

    assert respuesta.status_code == HTTPStatus.CREATED.value
    cuerpo = respuesta.json()
    assert "id" in cuerpo
    assert cuerpo["nombre"] == PERSONA_VALIDA["nombre"]
    assert cuerpo["programa"] == PERSONA_VALIDA["programa"]


def test_crear_persona_con_nombre_vacio_devuelve_422(cliente):
    respuesta = cliente.post(
        "/personas",
        json={"nombre": "", "programa": "Ingenieria de Sistemas"},
    )

    assert respuesta.status_code == HTTPStatus.UNPROCESSABLE_ENTITY.value


def test_actualizar_persona_devuelve_200(cliente):
    creada = _crear_persona(cliente)
    respuesta = cliente.put(
        f"/personas/{creada['id']}",
        json=PERSONA_ACTUALIZADA,
    )

    assert respuesta.status_code == HTTPStatus.OK.value
    cuerpo = respuesta.json()
    assert cuerpo["id"] == creada["id"]
    assert cuerpo["nombre"] == PERSONA_ACTUALIZADA["nombre"]
    assert cuerpo["programa"] == PERSONA_ACTUALIZADA["programa"]


def test_actualizar_persona_inexistente_devuelve_404(cliente):
    respuesta = cliente.put(f"/personas/{uuid4()}", json=PERSONA_ACTUALIZADA)

    assert respuesta.status_code == HTTPStatus.NOT_FOUND.value
    assert respuesta.json()["detail"] == "Persona no encontrada"


def test_borrar_persona_creada_devuelve_204(cliente):
    creada = _crear_persona(cliente)

    respuesta = cliente.delete(f"/personas/{creada['id']}")

    assert respuesta.status_code == HTTPStatus.NO_CONTENT.value
    consulta = cliente.get(f"/personas/{creada['id']}")
    assert consulta.status_code == HTTPStatus.NOT_FOUND.value


def test_borrar_persona_inexistente_devuelve_404(cliente):
    respuesta = cliente.delete(f"/personas/{uuid4()}")

    assert respuesta.status_code == HTTPStatus.NOT_FOUND.value
    assert respuesta.json()["detail"] == "Persona no encontrada"
