# Standard Imports
import logging
from logging import Logger
from datetime import datetime, timedelta
import random

# Third Party Imports
# import valkey
from pymongo import AsyncMongoClient
from beanie import init_beanie

# My Imports
from .models import User, Machine, Log
from .config import CONFIG_SETTINGS


logging.basicConfig(level=logging.INFO)
logger: Logger = logging.getLogger(__name__)


# async def get_valkey() -> AsyncGenerator[valkey.Valkey | Any, Any]:
#     try:
#         with valkey.Valkey(host="valkey") as kv:
#             yield kv
#     except valkey.ConnectionError:
#         logger.warning("Valkey connection failed, retrying...")
#         await asyncio.sleep(2)
#         yield get_valkey()


# ------------Init-Beanie-------------#
async def init_db() -> None:
    logger.info("Initializing database...")
    client: AsyncMongoClient = AsyncMongoClient(CONFIG_SETTINGS.DB_URI)
    await init_beanie(
        database=client["admin"],
        document_models=[User, Machine, Log],
    )
    logger.info("Database initialized")


# ------------Fake Data-------------#
async def create_sudo_user() -> None:
    sudo_user: User | None = await User.find_one(User.name == "sudo", User.admin == True, User.password == "sudo")
    if sudo_user is None:
        result = await User(name="sudo", password="sudo", admin=True).save()
        logger.info("Created sudo user")


async def create_plain_user() -> None:
    plain_user: User | None = await User.find_one(User.name == "user", User.admin == False, User.password == "user")
    if plain_user is None:
        result = await User(name="user", password="user", admin=False).save()
        logger.info("Created plain user")


adjectives: list[str] = [
    "adaptable",
    "adventurous",
    "affectionate",
    "ambitious",
    "amiable",
    "compassionate",
    "considerate",
    "courageous",
    "courteous",
    "diligent",
    "empathetic",
    "exuberant",
    "frank",
    "generous",
    "gregarious",
    "impartial",
    "intuitive",
    "inventive",
    "passionate",
    "persistent",
    "philosophical",
    "practical",
    "rational",
    "reliable",
    "resourceful",
    "sensible",
    "sincere",
    "sympathetic",
    "unassuming",
    "witty",
]

nouns: list[str] = [
    "area",
    "book",
    "business",
    "case",
    "child",
    "company",
    "country",
    "day",
    "eye",
    "fact",
    "family",
    "government",
    "group",
    "hand",
    "home",
    "job",
    "life",
    "lot",
    "man",
    "money",
    "month",
    "mother",
    "mr",
    "night",
    "number",
    "part",
    "people",
    "place",
    "point",
    "problem",
]


async def generate_machine_name() -> str:
    adjective: str = random.choice(adjectives)
    noun: str = random.choice(nouns)
    return f"{adjective}-{noun}"


async def create_fake_machines() -> None:
    check_db: list[Machine] = await Machine.find_all().to_list()
    if len(check_db) >= 50:
        return None
    fake_machines: list[Machine] = [
        Machine(
            name=await generate_machine_name(),
            joined_condition=random.randint(0, 5),
            special_note=random.choice(
                [
                    "What a great machine!",
                    "With the Frizz? No way!",
                    "I'm a machine!",
                    None,
                    None,
                ]
            ),
            joined_time=datetime.now() - timedelta(days=random.randint(0, 365)),
        )
        for _ in range(50)
    ]
    await Machine.insert_many(fake_machines)
    logger.info(f"Created {len(fake_machines)} fake machines")


async def generate_user_name() -> str:
    adjective: str = random.choice(adjectives)
    noun: str = random.choice(nouns)
    return f"{adjective.title()} {noun.title()}"


async def create_fake_users() -> None:
    check_db: list[User] = await User.find_all().to_list()
    if len(check_db) >= 20:
        return None

    fake_users: list[User] = [
        User(
            name=await generate_user_name(),
            password="password",
            admin=random.random() < 0.25,
            joined_time=datetime.now() - timedelta(days=random.randint(0, 365)),
        )
        for _ in range(18)
    ]
    await User.insert_many(fake_users)
    logger.info(f"Created {len(fake_users)} fake users")


async def load_fake_data() -> None:
    if CONFIG_SETTINGS.FAKE_DATA:
        await create_sudo_user()
        await create_plain_user()
        await create_fake_machines()
        await create_fake_users()
