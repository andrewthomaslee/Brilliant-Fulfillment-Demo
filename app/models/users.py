from typing import Any
from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field
from beanie import Document, Link, Indexed, TimeSeriesConfig, Granularity


class User(Document):
    joined_time: datetime = datetime.now(timezone.utc)
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
