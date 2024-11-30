from pydantic import BaseModel


class User(BaseModel):
    """A pydantic model for users."""

    id: int
    username: str
    hashed_password: str

    class Config:
        """Pydantic configuration."""

        from_attributes = True
