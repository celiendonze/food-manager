"""The API for interacting with the database."""
from sqlalchemy.orm import Session
import pandas as pd
from dotenv import load_dotenv
from food_manager.db.base import Base

from food_manager.db.food_item import FoodItem
from loguru import logger

load_dotenv()


class Api:
    """The API for interacting with the database."""

    def __init__(self, session: Session) -> None:
        """Initialize the API."""
        self.session = session
        self.create_tables()

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
            food_item = FoodItem(name=name, quantity=quantity, date_added=now)
            self.session.add(food_item)
            self.session.commit()
        logger.info(f"Added {quantity} {name} to the database.")
        return food_item

    def remove_food_item_by_id(self, id: int) -> FoodItem:
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

    def remove_food_item_by_name(self, name: str) -> None:
        with self.session.begin():
            self.session.query(FoodItem).filter(FoodItem.name == name).delete()
        logger.info(f"Removed food item with name {name} from the database.")

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
        """Get all food items in the database."""
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
