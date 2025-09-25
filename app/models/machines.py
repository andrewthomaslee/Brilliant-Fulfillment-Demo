# Standard Imports
from typing import Any, Annotated, Literal
from datetime import datetime

# Third Party Imports
from pydantic import BaseModel, Field
from beanie import Document

# My Imports
from ..utils import current_time


class Machine(Document):
    joined_time: datetime = Field(default_factory=current_time)
    name: str
    joined_condition: int = Field(ge=0, le=5)
    special_note: str | None = None

    class Settings:
        name = "machines"


class MachineQuery(BaseModel):
    operator: Literal["gte", "lte", "eq", "ne", "lt", "gt"] = Field(default="eq")
    joined_time: datetime | None = Field(default=None)
    name: str | None = Field(default=None, min_length=1)
    joined_condition: int | None = Field(default=None, ge=0, le=5)


class MachineCreate(BaseModel):
    name: str
    joined_condition: int = Field(ge=0, le=5)
    special_note: str | None = None


class MachineUpdate(BaseModel):
    name: str | None = None
    joined_condition: int | None = None
    special_note: str | None = None
