from typing import Any
from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field
from beanie import Document, Link, Indexed, TimeSeriesConfig, Granularity

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
    ts: datetime = Field(default_factory=datetime.now)
    user: Link[User]
    machine: Link[Machine]
    active: bool
    prompt: Prompt

    class Settings:
        name = "logs"
        timeseries = TimeSeriesConfig(
            time_field="ts",
            granularity=Granularity.seconds,
        )


class LogGet(BaseModel):
    ts: datetime | None = None
    user: User | None = None
    machine: Machine | None = None
    active: bool | None = None
    prompt: Prompt | None = None


class LogCreate(BaseModel):
    user: User
    machine: Machine
    active: bool
    prompt: Prompt
