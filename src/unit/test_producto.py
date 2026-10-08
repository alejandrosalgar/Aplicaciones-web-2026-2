from http import HTTPStatus
from uuid import uuid4

from fastapi import HTTPException

from src.crud import producto as crud_producto

PRODUCTO_VALIDO = {
    "nombre": "Cuaderno de pruebas",
    "precio": "12500.50",
}

PRODUCTO_ACTUALIZADO = {
    "nombre": "Cuaderno actualizado",
    "precio": "14900.00",
}


def _crear_producto(cliente, datos=None):
    respuesta = cliente.post("/productos/", json=datos or PRODUCTO_VALIDO)
    assert respuesta.status_code == HTTPStatus.CREATED.value
    return respuesta.json()


def test_listar_productos_devuelve_200_y_lista(cliente):
    _crear_producto(cliente)

    respuesta = cliente.get("/productos/")

    assert respuesta.status_code == HTTPStatus.OK.value
    cuerpo = respuesta.json()
    assert isinstance(cuerpo, list)
    assert len(cuerpo) == 1
    assert cuerpo[0]["nombre"] == PRODUCTO_VALIDO["nombre"]
    assert cuerpo[0]["precio"] == PRODUCTO_VALIDO["precio"]


def test_listar_productos_devuelve_503_si_falla_la_consulta(
    cliente, monkeypatch
):
    def fallar_listado(_db):
        raise HTTPException(
            status_code=HTTPStatus.SERVICE_UNAVAILABLE.value,
            detail="Servicio de productos no disponible",
        )

    monkeypatch.setattr(crud_producto, "listar_productos", fallar_listado)

    respuesta = cliente.get("/productos/")

    assert respuesta.status_code == HTTPStatus.SERVICE_UNAVAILABLE.value
    assert respuesta.json() == {
        "detail": "Servicio de productos no disponible"
    }


def test_obtener_producto_existente_devuelve_200(cliente):
    creado = _crear_producto(cliente)

    respuesta = cliente.get(f"/productos/{creado['id']}")

    assert respuesta.status_code == HTTPStatus.OK.value
    cuerpo = respuesta.json()
    assert cuerpo["id"] == creado["id"]
    assert cuerpo["nombre"] == PRODUCTO_VALIDO["nombre"]
    assert cuerpo["precio"] == PRODUCTO_VALIDO["precio"]


def test_obtener_producto_inexistente_devuelve_404(cliente):
    respuesta = cliente.get(f"/productos/{uuid4()}")

    assert respuesta.status_code == HTTPStatus.NOT_FOUND.value
    assert respuesta.json() == {"detail": "Producto no encontrado"}


def test_crear_producto_valido_devuelve_201(cliente):
    respuesta = cliente.post("/productos/", json=PRODUCTO_VALIDO)

    assert respuesta.status_code == HTTPStatus.CREATED.value
    cuerpo = respuesta.json()
    assert cuerpo["id"]
    assert cuerpo["nombre"] == PRODUCTO_VALIDO["nombre"]
    assert cuerpo["precio"] == PRODUCTO_VALIDO["precio"]


def test_crear_producto_sin_campos_obligatorios_devuelve_422(cliente):
    respuesta = cliente.post("/productos/", json={})

    assert respuesta.status_code == HTTPStatus.UNPROCESSABLE_ENTITY.value
    errores = respuesta.json()["detail"]
    assert {error["loc"][-1] for error in errores} == {"nombre", "precio"}


def test_actualizar_producto_existente_devuelve_200(cliente):
    creado = _crear_producto(cliente)

    respuesta = cliente.put(
        f"/productos/{creado['id']}", json=PRODUCTO_ACTUALIZADO
    )

    assert respuesta.status_code == HTTPStatus.OK.value
    cuerpo = respuesta.json()
    assert cuerpo["id"] == creado["id"]
    assert cuerpo["nombre"] == PRODUCTO_ACTUALIZADO["nombre"]
    assert cuerpo["precio"] == PRODUCTO_ACTUALIZADO["precio"]


def test_actualizar_producto_inexistente_devuelve_404(cliente):
    respuesta = cliente.put(
        f"/productos/{uuid4()}", json=PRODUCTO_ACTUALIZADO
    )

    assert respuesta.status_code == HTTPStatus.NOT_FOUND.value
    assert respuesta.json() == {"detail": "Producto no encontrado"}


def test_eliminar_producto_existente_devuelve_200_y_mensaje(cliente):
    creado = _crear_producto(cliente)

    respuesta = cliente.delete(f"/productos/{creado['id']}")

    assert respuesta.status_code == HTTPStatus.OK.value
    assert respuesta.json() == {"mensaje": "Producto eliminado"}


def test_eliminar_producto_inexistente_devuelve_404(cliente):
    respuesta = cliente.delete(f"/productos/{uuid4()}")

    assert respuesta.status_code == HTTPStatus.NOT_FOUND.value
    assert respuesta.json() == {"detail": "Producto no encontrado"}