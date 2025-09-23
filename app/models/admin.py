from datetime import datetime, timezone


from pydantic import BaseModel
from beanie import Document


class User(Document):
    create_at: datetime = datetime.now(timezone.utc)
    admin: bool = False
    name: str
    password: str

    class Settings:
        name = "users"


class UserRequest(BaseModel):
    admin: bool | None = None
    name: str | None = None
    password: str | None = None


# class Machines(BaseModel):
#     machine_id: str = Field(default_factory=lambda: str(uuid4()))
#     created_time: datetime = Field(default_factory=datetime.now)
#     hostname: str
#     condition: int
#     special_note: str


# class Logs(BaseModel):
#     created_time: datetime = Field(default_factory=datetime.now)
#     user_id: str
#     machine_id: str
