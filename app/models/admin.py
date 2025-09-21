from uuid import uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field


class Users(SQLModel, table=True):
    user_id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str
    admin: bool
    password: str
    create_time: datetime = Field(default_factory=datetime.now)


class UserCreate(Users):
    pass


class Machines(SQLModel, table=True):
    machine_id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    hostname: str
    created_time: datetime = Field(default_factory=datetime.now)
    condition: int
    special_note: str


class Prompts(SQLModel):
    condition: int
    battery: str
    task: str
    special_note: str


class Logs(SQLModel, table=True):
    logged_at: datetime = Field(default_factory=datetime.now)
    user_id: str
    machine_id: str
    active: bool
    prompts: Prompts
