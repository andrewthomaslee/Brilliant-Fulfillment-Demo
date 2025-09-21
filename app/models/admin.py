from pydantic import BaseModel, Field
from uuid import uuid4
from datetime import datetime


class User(BaseModel):
    _id: str = Field(default_factory=lambda: str(uuid4()), alias="id")
    name: str
    admin: bool
    password: str
    create_time: datetime = Field(default_factory=datetime.now)


class Machine(BaseModel):
    _id: str = Field(default_factory=lambda: str(uuid4()), alias="id")
    hostname: str
    created_time: datetime = Field(default_factory=datetime.now)
    condition: int
    special_note: str


class Prompts(BaseModel):
    condition: int
    battery: str
    task: str
    special_note: str


class Log(BaseModel):
    logged_at: datetime = Field(default_factory=datetime.now)
    user_id: str
    machine_id: str
    active: bool
    prompts: dict[str, str]
