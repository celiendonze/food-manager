"""FastAPI app root."""
from typing import Annotated
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Path, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from food_manager.api import Api
from food_manager.db import SessionLocal
from food_manager.schema.food_item import FoodItem
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="./app/static"), name="static")
templates = Jinja2Templates(directory="./app/templates")


def get_session():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def root(request: Request, session: Session = Depends(get_session)):
    """Root endpoint. display simple frontend."""
    all_food_items = await get_food_items(session=session)
    for food_item in all_food_items:
        food_item["date_added"] = food_item["date_added"].split(" ")[0]
    return templates.TemplateResponse(
        "index.html", {"request": request, "all_food_items": all_food_items}
    )


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


class FoodItemRequest(BaseModel):
    """A request for a food item."""

    name: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)


@app.post("/food_item")
async def add_food_item(
    food_item: FoodItemRequest, session: Session = Depends(get_session)
):
    """Add a food item."""
    api = Api(session=session)
    new_food_item = api.add_food_item(name=food_item.name, quantity=food_item.quantity)
    return {"message": "Food item added successfully!", "food_item": new_food_item}


@app.put("/food_item/{id}/{quantity}")
async def update_food_item_quantity(
    id: int,
    quantity: Annotated[int, Path(title="The new quantity.", gt=0)],
    session: Session = Depends(get_session),
):
    """Update a food item."""
    api = Api(session=session)
    food_item = api.update_food_item_quantity(id=id, quantity=quantity)
    return {"message": "Food item updated successfully!", "food_item": food_item}


@app.delete("/food_item/{id}")
async def remove_food_item_by_id(id: int, session: Session = Depends(get_session)):
    """Remove a food item by id."""
    api = Api(session=session)
    food_item = api.remove_food_item_by_id(id=id)
    return {"message": "Food item removed successfully!", "food_item": food_item}
