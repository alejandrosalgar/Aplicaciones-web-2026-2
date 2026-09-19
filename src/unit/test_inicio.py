def test_inicio_devuelve_200(cliente):
    respuesta = cliente.get("/")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert "docs" in cuerpo
    assert cuerpo["docs"] == "/docs"
