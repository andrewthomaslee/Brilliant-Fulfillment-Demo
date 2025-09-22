from uuid import uuid4
from datetime import datetime
from pydantic import BaseModel, Field


class Users(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid4()))
    create_time: datetime = Field(default_factory=datetime.now)
    name: str
    admin: bool
    password: str


class Machines(BaseModel):
    machine_id: str = Field(default_factory=lambda: str(uuid4()))
    created_time: datetime = Field(default_factory=datetime.now)
    hostname: str
    condition: int
    special_note: str


class Logs(BaseModel):
    created_time: datetime = Field(default_factory=datetime.now)
    user_id: str
    machine_id: str
