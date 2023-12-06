"""Test the Python API."""
from food_manager.api import Api
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pytest import fixture


@fixture
def api():
    """Create an API fixture."""
    return Api(session=sessionmaker(bind=create_engine("sqlite:///:memory:"))())


def test_get_all_food_items(api: Api):
    """Test getting all food items."""
    for i in range(10):
        assert len(api.get_all_food_items()) == i
        api.add_food_item(name="test", quantity=1)


def test_add_food_item(api: Api):
    """Test adding a food item."""
    food_item = api.add_food_item(name="test", quantity=1)
    assert len(api.get_all_food_items()) == 1
    assert food_item.id == 1
    assert food_item.name == "test"
    assert food_item.quantity == 1


def test_remove_food_item_by_id(api: Api):
    """Test removing a food item by id."""
    api.add_food_item(name="test", quantity=1)
    food_item = api.remove_food_item_by_id(id=1)
    assert food_item.id == 1
    assert food_item.name == "test"
    assert food_item.quantity == 1
    assert len(api.get_all_food_items()) == 0
