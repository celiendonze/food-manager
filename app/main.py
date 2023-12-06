"""FastAPI app root."""

from typing import Literal
from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from food_manager.api import Api
from food_manager.db import SessionLocal
from sqlalchemy.orm import Session

from food_manager.schema.food_item import FoodItem

load_dotenv()

app = FastAPI()


def get_session():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Hello from the Food Manager API!"}


@app.get("/food_items")
async def get_food_items(session: Session = Depends(get_session)) -> list[FoodItem]:
    """Get food items."""
    api = Api(session=session)
    return api.get_all_food_items().to_dict(orient="records")


@app.get("/food_item/{id}")
async def get_food_items_by_id(
    id: int, session: Session = Depends(get_session)
) -> FoodItem:
    """Get food items."""
    api = Api(session=session)
    return api.get_food_item_by_id(id=id)


@app.post("/food_item")
async def add_food_item(
    name: str,
    quantity: int,
    type: Literal["unit", "liquid", "other"] = "unit",
    session: Session = Depends(get_session),
):
    """Add a food item."""
    api = Api(session=session)
    api.add_food_item(name=name, quantity=quantity)
    return {"message": "Food item added successfully!"}


@app.delete("/food_item/{id}")
async def remove_food_item_by_id(id: int, session: Session = Depends(get_session)):
    """Remove a food item by id."""
    api = Api(session=session)
    api.remove_food_item_by_id(id=id)
    return {"message": "Food item removed successfully!"}
