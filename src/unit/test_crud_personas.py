from uuid import uuid4

from src.crud.personas import obtener_por_id


class DbFalsa:
    def get(self, _modelo, _identificador):
        return None


def test_obtener_por_id_devuelve_none_si_no_existe():
    resultado = obtener_por_id(DbFalsa(), uuid4())
    assert resultado is None
