from typing import Any
from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field
from beanie import Document, Link, Indexed, TimeSeriesConfig, Granularity


class Machine(Document):
    joined_time: datetime = datetime.now(timezone.utc)
    name: str
    joined_condition: int = Field(ge=0, le=5)
    special_note: str | None = None

    class Settings:
        name = "machines"


class MachineGet(BaseModel):
    joined_time: datetime | None = None
    name: str | None = None
    joined_condition: int | None = None


class MachineCreate(BaseModel):
    name: str
    joined_condition: int = Field(ge=0, le=5)
    special_note: str | None = None


class MachineUpdate(BaseModel):
    name: str | None = None
    joined_condition: int | None = None
    special_note: str | None = None
