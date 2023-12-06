"""Pydantic models for food items."""
from pydantic import BaseModel


class FoodItem(BaseModel):
    """A pydantic model for food items."""

    id: int
    name: str
    quantity: int
    date_added: str

    class Config:
        """Pydantic configuration."""

        from_attributes = True
