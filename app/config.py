from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR: Path = Path(__file__).parent


class connectionSettings(BaseSettings):
    DB_URI: str = "mongodb://localhost:27017"
    KV_URI: str = "valkey://localhost:6379"
    SECRET_KEY: str = "secret-key"
    FAKE_DATA: bool = False


CONFIG_SETTINGS: connectionSettings = connectionSettings()
