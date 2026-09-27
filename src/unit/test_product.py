#INVALIDOS
from decimal import Decimal
from uuid import uuid4


def test_crear_product_con_costo_invalido_devuelve_422(cliente):
    datos_invalidos = {
        "name": "Camiseta Oversize",
        "description": "Camiseta de algodon 100%",
        "category": "Ropa",
        "sku": "CAM-001",
        "cost": 0,
        "stock": 10,
    }

    response = cliente.post("/products", json=datos_invalidos)

    assert response.status_code == 422

def test_crear_product_con_dato_invalido_devuelve_422(cliente):
    datos_invalidos = {
        "name": "Camiseta Oversize",
        "description": "Camiseta de algodon 100%",
        "category": "Ropa",
        "sku": "CAM-001",
        "cost": "mil",
        "stock": 29,
    }

    response = cliente.post("/products", json=datos_invalidos)
    assert response.status_code == 422

def test_obtener_product_con_id_inexistente_devuelve_404(cliente):
    id_random = uuid4()

    response = cliente.get(f"/products/{id_random}")

    assert response.status_code == 404
    body = response.json()
    assert body["detail"]=="Producto no encontrado"


def test_eliminar_product_sin_id_devuelve_405(cliente):
    response = cliente.delete("/products")

    assert response.status_code == 405


def test_actualizar_product_con_id_inexistente_devuelve_404(cliente):
    id_random = uuid4()
    datos_actualizados = {
        "name": "Camiseta Slim Fit",
        "description": "Camiseta de algodon 100% ajustada",
        "category": "Ropa",
        "sku": "CAM-002",
        "cost": 35000,
        "stock": 15,
    }

    response = cliente.put(f"/products/{id_random}", json=datos_actualizados)

    assert response.status_code == 404
    body = response.json()
    assert body["detail"]=="Producto no encontrado"

def test_eliminar_product_inexistente_devuelve_404(cliente):
    id_random = uuid4()

    response = cliente.delete(f"/products/{id_random}")

    assert response.status_code == 404
    body = response.json()
    assert body["detail"] == "Producto no encontrado"
#VALIDOS

def test_crear_product_valido_devuelve_201(cliente):
    datos_validos = {
        "name": "Camiseta Oversize",
        "description": "Camiseta de algodon 100%",
        "category": "Ropa",
        "sku": "CAM-001",
        "cost": 30000,
        "stock": 10,
    }

    response = cliente.post("/products", json=datos_validos)

    assert response.status_code == 201
    cuerpo = response.json()
    assert "id" in cuerpo
    assert cuerpo["name"] == datos_validos["name"]
    assert cuerpo["description"] == datos_validos["description"]
    assert cuerpo["category"] == datos_validos["category"]
    assert cuerpo["sku"] == datos_validos["sku"]
    assert Decimal(cuerpo["cost"]) == Decimal(str(datos_validos["cost"]))
    assert cuerpo["stock"] == datos_validos["stock"]

def test_obtener_product_existente_correcto_devuelve_200(cliente):
    datos_validos = {
        "name": "Camiseta Oversize",
        "description": "Camiseta de algodon 100%",
        "category": "Ropa",
        "sku": "CAM-001",
        "cost": 30000,
        "stock": 10,
    }

    create = cliente.post("/products", json=datos_validos)
    product_id = create.json()["id"]

    response = cliente.get(f"/products/{product_id}")

    assert response.status_code == 200
    cuerpo = response.json()
    assert cuerpo["id"] == product_id
    assert cuerpo["name"] == datos_validos["name"]
    assert cuerpo["description"] == datos_validos["description"]
    assert cuerpo["category"] == datos_validos["category"]
    assert cuerpo["sku"] == datos_validos["sku"]
    assert Decimal(cuerpo["cost"]) == Decimal(str(datos_validos["cost"]))
    assert cuerpo["stock"] == datos_validos["stock"]

def test_obtener_una_lista_de_productos_devuelve_200(cliente):
    datos_validos = {
        "name": "Camiseta Oversize",
        "description": "Camiseta de algodon 100%",
        "category": "Ropa",
        "sku": "CAM-001",
        "cost": 30000,
        "stock": 10,
    }

    cliente.post("/products", json=datos_validos)
    response = cliente.get("/products")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) >= 1
    assert body[0]["name"] == datos_validos["name"]

def test_editar_product_existente_devuelve_200(cliente):
    datos_validos = {
        "name": "Camiseta Oversize",
        "description": "Camiseta de algodon 100%",
        "category": "Ropa",
        "sku": "CAM-001",
        "cost": 30000,
        "stock": 10,
    }

    create = cliente.post("/products", json=datos_validos)
    product_id = create.json()["id"]

    datos_actualizados = {
        "name": "Camiseta Slim Fit",
        "description": "Camiseta de algodon 100% ajustada",
        "category": "Ropa",
        "sku": "CAM-002",
        "cost": 35000,
        "stock": 15,
    }

    response = cliente.put(f"/products/{product_id}", json=datos_actualizados)

    assert response.status_code == 200
    cuerpo = response.json()
    assert cuerpo["id"] == product_id
    assert cuerpo["name"] == datos_actualizados["name"]
    assert cuerpo["description"] == datos_actualizados["description"]
    assert cuerpo["category"] == datos_actualizados["category"]
    assert cuerpo["sku"] == datos_actualizados["sku"]
    assert Decimal(cuerpo["cost"]) == Decimal(str(datos_actualizados["cost"]))
    assert cuerpo["stock"] == datos_actualizados["stock"]

def test_eliminar_product_existente_devuelve_204(cliente):
    datos_validos = {
        "name": "Camiseta Oversize",
        "description": "Camiseta de algodon 100%",
        "category": "Ropa",
        "sku": "CAM-002",
        "cost": 30000,
        "stock": 10,
    }

    creado = cliente.post("/products", json=datos_validos)
    product_id = creado.json()["id"]

    response = cliente.delete(f"/products/{product_id}")

    assert response.status_code == 204

    verificacion = cliente.get(f"/products/{product_id}")
    assert verificacion.status_code == 404
