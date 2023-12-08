"""Test the FastAPI app."""
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, get_session

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_session():
    """Override the get_session function."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


app.dependency_overrides[get_session] = override_get_session
client = TestClient(app)


def test_root():
    """Test the root endpoint."""
    response: Response = client.get("/")
    assert response.status_code == 200


def test_get_food_items():
    """Test getting all food items."""
    response: Response = client.get("/food_items")
    assert response.status_code == 200
    assert response.json() == []


def test_add_food_item():
    """Test adding a food item."""
    response: Response = client.post(
        "/food_item", json={"name": "apple", "quantity": 5}
    )
    assert response.status_code == 200
