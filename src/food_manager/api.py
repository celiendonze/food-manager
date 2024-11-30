"""The API for interacting with the database."""

import pandas as pd
from dotenv import load_dotenv
from loguru import logger
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from food_manager.db.models import Base, FoodItem, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv(override=True)


class Api:
    """The API for interacting with the database."""

    def __init__(self, session: Session, current_user_id: int = None) -> None:
        """Initialize the API."""
        self.session = session
        self.create_tables()
        self.current_user_id = current_user_id

    def set_current_user(self, username: str) -> None:
        """Set the current user id.

        Args:
            username (str): The username of the user.
        """
        with self.session.begin():
            user = (
                self.session.query(User).filter(User.username == username).one_or_none()
            )
            if user is None:
                logger.debug(f"User with username {username} does not exist.")
            else:
                logger.debug(f"Set current user id to {user}.")
                self.current_user_id = int(user.id)

    def create_user(self, username: str, password: str) -> None:
        """Create a user in the database.

        Args:
            username (str): The username of the user.
            password (str): The password of the user.
        """
        with self.session.begin():
            if self.session.query(User).filter(User.username == username).one_or_none():
                logger.debug(f"User with username {username} already exists.")
                raise ValueError(f"User with username {username} already exists.")
            hased_password = pwd_context.hash(password)
            user = User(username=username, hashed_password=hased_password)
            self.session.add(user)
            self.session.commit()

    def get_all_users(self) -> pd.DataFrame:
        """Get all users in the database.

        Returns:
            pd.DataFrame: All users in the database.
        """
        with self.session.begin():
            users_df = pd.read_sql_table(
                table_name="user", con=self.session.connection()
            )
        logger.info("Retrieved all users from the database.")
        return users_df

    def get_user_by_username(self, username: str) -> User:
        """Get a user by username.

        Args:
            username (str): The username of the user.

        Returns:
            User: The user.
        """
        with self.session.begin():
            user = (
                self.session.query(User).filter(User.username == username).one_or_none()
            )
        if user is not None:
            logger.info(f"Retrieved user with username {username} from the database.")
        return user

    def add_food_item(self, name: str, quantity: int) -> FoodItem:
        """Add a food item to the database.

        Args:
            name (str): Name of the food item.
            quantity (int): Quantity of the food item.

        Returns:
            FoodItem: The added food item.
        """
        with self.session.begin():
            now = str(pd.Timestamp.utcnow())
            user = (
                self.session.query(User).filter(User.id == self.current_user_id).one()
            )
            food_item = FoodItem(
                name=name, quantity=quantity, date_added=now, user=user
            )
            self.session.add(food_item)
            self.session.commit()
        logger.info(f"Added {quantity} {name} to the database.")
        return food_item

    def update_food_item_quantity(self, id: int, quantity: int) -> FoodItem:
        """Update the quantity of a food item.

        Args:
            id (int): The id of the food item.
            quantity (int): The new quantity of the food item.

        Returns:
            FoodItem: The updated food item.
        """
        with self.session.begin():
            food_item = (
                self.session.query(FoodItem).filter(FoodItem.id == id).one_or_none()
            )
            if food_item is None:
                logger.info(f"Food item with id {id} does not exist.")
            else:
                food_item.quantity = quantity
                self.session.commit()
                logger.info(
                    f"Updated quantity of food item with id {id} to {quantity}."
                )
        return food_item

    def remove_food_item_by_id(self, id: int) -> FoodItem:
        """Remove a food item by id.

        Args:
            id (int): The id of the food item.

        Returns:
            FoodItem: The removed food item.
        """
        with self.session.begin():
            food_item = (
                self.session.query(FoodItem).filter(FoodItem.id == id).one_or_none()
            )
            if food_item is None:
                logger.info(f"Food item with id {id} does not exist.")
            else:
                self.session.delete(food_item)
                logger.info(f"Removed food item with id {id} from the database.")
        return food_item

    def get_food_item_by_id(self, id: int) -> FoodItem:
        """Get a food item by id.

        Args:
            id (int): The id of the food item.

        Returns:
            FoodItem: The food item.
        """
        with self.session.begin():
            food_item = (
                self.session.query(FoodItem).filter(FoodItem.id == id).one_or_none()
            )
        logger.info(f"Retrieved food item with id {id} from the database.")
        return food_item

    def get_all_food_items(self) -> pd.DataFrame:
        """Get all food items in the database.

        Returns:
            pd.DataFrame: All food items in the database.
        """
        with self.session.begin():
            food_items_df = pd.read_sql_table(
                table_name="food_item", con=self.session.connection()
            )
        logger.info("Retrieved all food items from the database.")
        return food_items_df

    def create_tables(self) -> None:
        """Create all tables in the database."""
        with self.session.begin():
            Base.metadata.create_all(bind=self.session.connection())

    def drop_tables(self) -> None:
        """Drop all tables in the database."""
        with self.session.begin():
            Base.metadata.drop_all(bind=self.session.connection())
        logger.info("Dropped all tables in the database.")
