"""The API for interacting with the database."""
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker
import os
import pandas as pd
from dotenv import load_dotenv
from loguru import logger

from food_manager_api.db.food_item import FoodItem
from .db.utils import create_tables, drop_tables

load_dotenv()


class Api:
    """The API for interacting with the database."""

    def __init__(self, database_engine: Engine = None) -> None:
        """Initialize the API.

        Args:
            database_engine (Engine, optional): The database engine to use. Defaults to None.
        """
        if database_engine is not None:
            self.engine = database_engine
        else:
            db_path = os.getenv("DATABASE_PATH")
            logger.info(f"Using database at {db_path}")
            self.engine = create_engine(f"sqlite:///{db_path}")
        self._create_tables()

    def add_food_item(self, name: str, quantity: int) -> None:
        session = sessionmaker(bind=self.engine)()
        with session.begin():
            now = str(pd.Timestamp.utcnow())
            session.add(FoodItem(name=name, quantity=quantity, date_added=now))

    def remove_food_item(self, name: str) -> None:
        session = sessionmaker(bind=self.engine)()
        with session.begin():
            session.query(FoodItem).filter(FoodItem.name == name).delete()

    def get_all_food_items(self) -> pd.DataFrame:
        """Get all food items in the database."""
        food_items_df = pd.read_sql_table("food_item", self.engine)
        return food_items_df

    def _create_tables(self) -> None:
        """Create all tables in the database."""
        create_tables(self.engine)

    def _drop_tables(self) -> None:
        """Drop all tables in the database."""
        drop_tables(self.engine)
