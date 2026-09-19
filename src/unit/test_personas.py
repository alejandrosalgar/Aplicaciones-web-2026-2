from uuid import uuid4

PERSONA_VALIDA = {
    "nombre": "Ana Perez",
    "programa": "Ingenieria de Sistemas",
}


def test_crear_persona_devuelve_201(cliente):
    respuesta = cliente.post("/personas", json=PERSONA_VALIDA)

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert "id" in cuerpo
    assert cuerpo["nombre"] == PERSONA_VALIDA["nombre"]
    assert cuerpo["programa"] == PERSONA_VALIDA["programa"]


def test_crear_persona_con_nombre_vacio_devuelve_422(cliente):
    respuesta = cliente.post(
        "/personas",
        json={"nombre": "", "programa": "Ingenieria de Sistemas"},
    )

    assert respuesta.status_code == 422


def test_obtener_persona_inexistente_devuelve_404(cliente):
    respuesta = cliente.get(f"/personas/{uuid4()}")

    assert respuesta.status_code == 404


def test_listar_personas_devuelve_200_y_una_lista(cliente):
    cliente.post("/personas", json=PERSONA_VALIDA)
    respuesta = cliente.get("/personas")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert isinstance(cuerpo, list)
    assert len(cuerpo) == 1
    assert cuerpo[0]["nombre"] == PERSONA_VALIDA["nombre"]


def test_borrar_persona_creada_devuelve_204(cliente):
    creada = cliente.post("/personas", json=PERSONA_VALIDA)
    persona_id = creada.json()["id"]

    respuesta = cliente.delete(f"/personas/{persona_id}")

    assert respuesta.status_code == 204
    consulta = cliente.get(f"/personas/{persona_id}")
    assert consulta.status_code == 404
