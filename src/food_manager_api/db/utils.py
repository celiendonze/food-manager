"""Database utility functions."""
from sqlalchemy import Engine
from .base import Base
from loguru import logger


def create_tables(engine: Engine):
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")


def drop_tables(engine: Engine):
    """Drop all tables in the database."""
    Base.metadata.drop_all(bind=engine)
    logger.info("Database tables dropped")
