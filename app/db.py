# Standard Imports
from typing import AsyncGenerator, Any
import logging
from logging import Logger
from pydantic_settings import BaseSettings

# Third Party Imports
import valkey
from pymongo import AsyncMongoClient
from beanie import init_beanie

# My Imports
from .models import User, Machine, Log


logging.basicConfig(level=logging.INFO)
logger: Logger = logging.getLogger(__name__)


class connectionSettings(BaseSettings):
    DB_URI: str = "mongodb://localhost:27017"
    KV_URI: str = "valkey://localhost:6379"


conn_settings: connectionSettings = connectionSettings()


# async def get_valkey() -> AsyncGenerator[valkey.Valkey | Any, Any]:
#     try:
#         with valkey.Valkey(host="valkey") as kv:
#             yield kv
#     except valkey.ConnectionError:
#         logger.warning("Valkey connection failed, retrying...")
#         await asyncio.sleep(2)
#         yield get_valkey()


async def init_db() -> None:
    client: AsyncMongoClient = AsyncMongoClient(conn_settings.DB_URI)
    await init_beanie(
        database=client["admin"],
        document_models=[User, Machine, Log],
    )


async def create_sudo_user() -> None:
    sudo_user: User | None = await User.find_one(User.name == "sudo", User.admin == True, User.password == "root")
    if sudo_user is None:
        result = await User(name="sudo", password="root", admin=True).save()
        logger.info(f"Created sudo user: {result}")


async def create_plain_user() -> None:
    plain_user: User | None = await User.find_one(User.name == "user", User.admin == False, User.password == "plain")
    if plain_user is None:
        result = await User(name="user", password="plain", admin=False).save()
        logger.info(f"Created plain user: {result}")
