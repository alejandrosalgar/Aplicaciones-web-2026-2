from uuid import uuid4

from src.crud.product import get_product_by_id


class DbFalsa:
    def get(self, _model, _id):
        return None


def test_get_product_by_id_returns_none_if_not_exists():
    result = get_product_by_id(DbFalsa(), uuid4())
    assert result is None


