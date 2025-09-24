# Standard Imports
from typing import Annotated
from datetime import datetime
from enum import StrEnum

# Third Party Imports
from pydantic import BaseModel, Field, AfterValidator
from beanie import Document, Link, TimeSeriesConfig, Granularity

# My Imports
from ..utils import check_document_exists, current_time
from .users import User
from .machines import Machine


class Task(StrEnum):
    WAKE_UP = "wake_up"
    SLEEP = "sleep"
    WORK = "work"
    PLAY = "play"
    DRINK = "drink"
    EAT = "eat"
    SIT = "sit"
    STAND = "stand"


class Prompt(BaseModel):
    condition: int = Field(ge=0, le=5)
    battery: int = Field(ge=0, le=100)
    task: Task
    special_note: str | None = None


class Log(Document):
    ts: datetime = Field(default_factory=current_time)
    user: Annotated[Link[User], AfterValidator(check_document_exists)]
    machine: Annotated[Link[Machine], AfterValidator(check_document_exists)]
    active: bool
    prompt: Prompt

    class Settings:
        name = "logs"
        timeseries = TimeSeriesConfig(
            time_field="ts",
            granularity=Granularity.seconds,
        )


class LogQuery(BaseModel):
    gte: bool | None = Field(
        default=True,
        description="If True, `ts` is filtered as greater than or equal to. If False, values are filtered as less than or equal to.",
    )
    ts: datetime | None = None
    user: Annotated[Link[User], AfterValidator(check_document_exists)] | None = None
    machine: Annotated[Link[Machine], AfterValidator(check_document_exists)] | None = None
    active: bool | None = None
    prompt: Prompt | None = None


class LogCreate(BaseModel):
    user: Annotated[Link[User], AfterValidator(check_document_exists)]
    machine: Annotated[Link[Machine], AfterValidator(check_document_exists)]
    active: bool
    prompt: Prompt


class LogUpdate(BaseModel):
    user: Annotated[Link[User], AfterValidator(check_document_exists)] | None = None
    machine: Annotated[Link[Machine], AfterValidator(check_document_exists)] | None = None
    active: bool | None = None
    prompt: Prompt | None = None
