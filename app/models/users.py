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


class UserGet(BaseModel):
    admin: bool = False
    name: str | None
    password: str | None


class UserCreate(BaseModel):
    name: str
    password: str


class UserUpdate(BaseModel):
    admin: bool | None = None
    name: str | None = None
    password: str | None = None
