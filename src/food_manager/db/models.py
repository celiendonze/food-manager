from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base model."""


class User(Base):
    """User model."""

    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    hashed_password = Column(String)
    food_items = relationship("FoodItem", back_populates="user")


class FoodItem(Base):
    """Food item model."""

    __tablename__ = "food_item"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    quantity = Column(Integer)
    date_added = Column(DateTime)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="food_items")
