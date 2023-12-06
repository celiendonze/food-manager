"""Food item database model."""
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .base import Base


class FoodItem(Base):
    """A food item in the database."""

    __tablename__ = "food_item"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    quantity: Mapped[int] = mapped_column(Integer)
    date_added: Mapped[str] = mapped_column(String)

    def __repr__(self) -> str:
        return f"FoodItem(id={self.id!r}, name={self.name!r})"
