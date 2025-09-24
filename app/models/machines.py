# Standard Imports
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
    gte: bool | None = Field(
        default=True,
        description="If True, `joined_time` and `joined_condition` are filtered as greater than or equal to. If False, values are filtered as less than or equal to.",
    )
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
