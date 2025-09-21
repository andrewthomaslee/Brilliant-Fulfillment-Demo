import subprocess
import valkey
import logging
from logging import Logger
from time import sleep

from sqlmodel import Session, create_engine, SQLModel
from .config import DATABASE_URL, DATA_DIR


logging.basicConfig(level=logging.INFO)
logger: Logger = logging.getLogger(__name__)

engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:  # pyrefly: ignore
        yield session


def init_kv():
    subprocess.Popen(["valkey-server"], cwd=DATA_DIR)
    kv = valkey.Valkey()
    while True:
        try:
            if kv.ping():
                logger.info("Valkey is ready.")
                del kv
                break
        except valkey.exceptions.ConnectionError:
            pass
        logger.info("Waiting for Valkey to start...")
        sleep(1)
