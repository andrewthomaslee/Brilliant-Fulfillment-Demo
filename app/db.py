# Standard Imports
from typing import AsyncGenerator, Any
import asyncio
import logging
from logging import Logger
from pydantic_settings import BaseSettings

# Third Party Imports
import valkey
from pymongo import AsyncMongoClient
from beanie import init_beanie

# My Imports
from .models.admin import User


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
        document_models=[User],
    )
