"""FastAPI app root."""

import hashlib
import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Path, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_login import LoginManager
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from food_manager.api import Api
from food_manager.db import SessionLocal
from food_manager.schema.food_item import FoodItem


class NotAuthenticatedException(Exception):
    """Not authenticated exception."""


load_dotenv(override=True)

SECRET_KEY = os.getenv("SECRET_KEY")

app = FastAPI()
app.mount("/static", StaticFiles(directory="./app/static"), name="static")
templates = Jinja2Templates(directory="./app/templates")

manager = LoginManager(
    SECRET_KEY,
    "/login",
    use_cookie=True,
    not_authenticated_exception=NotAuthenticatedException,
)


def exc_handler(request, exc):
    """Handle exceptions for not logged in users."""
    return RedirectResponse(url="/login")


app.add_exception_handler(NotAuthenticatedException, exc_handler)


def get_session():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create a few test users
with SessionLocal() as session:
    api = Api(session=session)
    try:
        api.create_user(username="test1", password="test1")
        api.create_user(username="test2", password="test2")
        api.create_user(username="test3", password="test3")
    except ValueError:
        pass  # user already exists, ignore
logger.debug("Test user created.")


@manager.user_loader()
def load_user(username: str) -> str:
    """Load a user."""
    with SessionLocal() as session:
        api = Api(session=session)
        user = api.get_user_by_username(username=username)
        return str(user.username)


@app.post("/login")
async def login(
    data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    """Login endpoint."""
    username = data.username
    password = data.password
    logger.debug(f"Login attempt for user {username}.")
    api = Api(session=session)
    hashed_password = hashlib.sha512(password.encode()).hexdigest()
    user = api.get_user_by_username(username=username)
    if user is None or user.hashed_password != hashed_password:
        return {"message": "Invalid credentials"}

    access_token = manager.create_access_token(data=dict(sub=user.username))
    # response is the token and a redirect to the root
    # response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response = JSONResponse(
        content={"message": "Login successful!", "token": access_token}
    )
    manager.set_cookie(response=response, token=access_token)

    return response


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login endpoint."""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/logout")
async def logout():
    """Logout endpoint."""
    response = RedirectResponse(url="/login")
    # delete the cookie
    manager.set_cookie(response=response, token="")
    return response


@app.get("/", response_class=HTMLResponse)
async def root(
    request: Request,
    username=Depends(manager),
    session: Session = Depends(get_session),
):
    """Root endpoint. display simple frontend."""
    api = Api(session=session)
    api.set_current_user(username=username)
    all_food_items = await get_food_items(username=username, session=session)
    for food_item in all_food_items:
        food_item["date_added"] = food_item["date_added"].split(" ")[0]
    return templates.TemplateResponse(
        name="index.html",
        context={
            "request": request,
            "username": username,
            "all_food_items": all_food_items,
        },
    )


@app.get("/food_items")
async def get_food_items(
    username=Depends(manager),
    session: Session = Depends(get_session),
) -> list[FoodItem]:
    """Get food items."""
    api = Api(session=session)
    api.set_current_user(username=username)
    return api.get_all_food_items().to_dict(orient="records")


@app.get("/food_item/{id}")
async def get_food_items_by_id(
    id: int,
    username=Depends(manager),
    session: Session = Depends(get_session),
) -> FoodItem:
    """Get food items."""
    api = Api(session=session)
    api.set_current_user(username=username)
    return api.get_food_item_by_id(id=id)


class FoodItemRequest(BaseModel):
    """A request for a food item."""

    name: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)


@app.post("/food_item")
async def add_food_item(
    food_item: FoodItemRequest,
    username=Depends(manager),
    session: Session = Depends(get_session),
):
    """Add a food item."""
    api = Api(session=session)
    api.set_current_user(username=username)
    new_food_item = api.add_food_item(name=food_item.name, quantity=food_item.quantity)
    return {"message": "Food item added successfully!", "food_item": new_food_item}


@app.put("/food_item/{id}/{quantity}")
async def update_food_item_quantity(
    id: int,
    quantity: Annotated[int, Path(title="The new quantity.", gt=0)],
    username=Depends(manager),
    session: Session = Depends(get_session),
):
    """Update a food item."""
    api = Api(session=session)
    api.set_current_user(username=username)
    food_item = api.update_food_item_quantity(id=id, quantity=quantity)
    return {"message": "Food item updated successfully!", "food_item": food_item}


@app.delete("/food_item/{id}")
async def remove_food_item_by_id(
    id: int,
    username=Depends(manager),
    session: Session = Depends(get_session),
):
    """Remove a food item by id."""
    api = Api(session=session)
    api.set_current_user(username=username)
    food_item = api.remove_food_item_by_id(id=id)
    return {"message": "Food item removed successfully!", "food_item": food_item}
