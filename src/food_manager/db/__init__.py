"""DataBase related functions."""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

database_url = os.getenv("DATABASE_URL")
if database_url is not None:
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
