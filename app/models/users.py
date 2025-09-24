# Standard Imports
from datetime import datetime

# Third Party Imports
from pydantic import BaseModel, Field
from beanie import Document

# My Imports
from ..utils import current_time


class User(Document):
    joined_time: datetime = Field(default_factory=current_time)
    admin: bool = False
    name: str
    password: str

    class Settings:
        name = "users"


class UserQuery(BaseModel):
    gte: bool | None = Field(
        default=True,
        description="If True, `joined_time` is filtered as greater than or equal to. If False, value is filtered as less than or equal to.",
    )
    joined_time: datetime | None = None
    admin: bool | None = False
    name: str | None
    password: str | None


class UserCreate(BaseModel):
    name: str
    password: str


class UserUpdate(BaseModel):
    admin: bool | None = None
    name: str | None = None
    password: str | None = None
