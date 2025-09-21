from uuid import uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field


class Users(SQLModel, table=True):
    user_id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    create_time: datetime = Field(default_factory=datetime.now)
    name: str
    admin: bool
    password: str


class Machines(SQLModel, table=True):
    machine_id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    created_time: datetime = Field(default_factory=datetime.now)
    hostname: str
    condition: int
    special_note: str
