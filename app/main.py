"""FastAPI app root."""

import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Path, Request, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# from fastapi_login import LoginManager
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from food_manager.api import Api
from food_manager.db import SessionLocal
from food_manager.schema.food_item import FoodItem
from food_manager.schema.token import Token, TokenData
from food_manager.schema.user import User

load_dotenv(override=True)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()
app.mount("/static", StaticFiles(directory="./app/static"), name="static")
templates = Jinja2Templates(directory="./app/templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# manager = LoginManager(SECRET_KEY, "/login")


def get_session():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create a test user
with SessionLocal() as session:
    api = Api(session=session)
    api.create_user(username="test", password="test")


def verify_password(plain_password: str | bytes, hashed_password: str | bytes):
    """Verify a password.

    Args:
        plain_password (str | bytes): The plain password.
        hashed_password (str | bytes): The hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Get a password hash."""
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str):
    """Authenticate a user."""
    api = Api(session=SessionLocal())
    user = api.get_user_by_username(username=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create an access token.

    Args:
        data (dict): The data to encode.
        expires_delta (timedelta | None): The expiration delta.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
) -> User:
    """Get the current user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.InvalidTokenError:
        raise credentials_exception
    user = Api(session=session).get_user_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get the current active user."""
    # if current_user.disabled:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    """Login endpoint."""
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """Login for access token endpoint."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Read the current user."""
    return current_user


@app.get("/", response_class=HTMLResponse)
async def root(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
):
    """Root endpoint. display simple frontend."""
    all_food_items = await get_food_items(session=session)
    for food_item in all_food_items:
        food_item["date_added"] = food_item["date_added"].split(" ")[0]
    return templates.TemplateResponse("index.html", {"all_food_items": all_food_items})


@app.get("/food_items")
async def get_food_items(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
) -> list[FoodItem]:
    """Get food items."""
    api = Api(session=session)
    return api.get_all_food_items().to_dict(orient="records")


@app.get("/food_item/{id}")
async def get_food_items_by_id(
    token: Annotated[str, Depends(oauth2_scheme)],
    id: int,
    session: Session = Depends(get_session),
) -> FoodItem:
    """Get food items."""
    user = await get_current_user(token=token, session=session)
    api = Api(session=session)
    api.set_current_user(username=user.username)
    return api.get_food_item_by_id(id=id)


class FoodItemRequest(BaseModel):
    """A request for a food item."""

    name: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)


@app.post("/food_item")
async def add_food_item(
    token: Annotated[str, Depends(oauth2_scheme)],
    food_item: FoodItemRequest,
    session: Session = Depends(get_session),
):
    """Add a food item."""
    user = await get_current_user(token=token, session=session)
    api = Api(session=session)
    api.set_current_user(username=user.username)
    new_food_item = api.add_food_item(name=food_item.name, quantity=food_item.quantity)
    return {"message": "Food item added successfully!", "food_item": new_food_item}


@app.put("/food_item/{id}/{quantity}")
async def update_food_item_quantity(
    token: Annotated[str, Depends(oauth2_scheme)],
    id: int,
    quantity: Annotated[int, Path(title="The new quantity.", gt=0)],
    session: Session = Depends(get_session),
):
    """Update a food item."""
    user = await get_current_user(token=token, session=session)
    api = Api(session=session)
    api.set_current_user(username=user.username)
    food_item = api.update_food_item_quantity(id=id, quantity=quantity)
    return {"message": "Food item updated successfully!", "food_item": food_item}


@app.delete("/food_item/{id}")
async def remove_food_item_by_id(
    token: Annotated[str, Depends(oauth2_scheme)],
    id: int,
    session: Session = Depends(get_session),
):
    """Remove a food item by id."""
    user = await get_current_user(token=token, session=session)
    api = Api(session=session)
    api.set_current_user(username=user.username)
    food_item = api.remove_food_item_by_id(id=id)
    return {"message": "Food item removed successfully!", "food_item": food_item}
