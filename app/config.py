from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR: Path = Path(__file__).parent


class ConfigSettings(BaseSettings):
    DB_URI: str = "mongodb://localhost:27017"
    KV_URI: str = "valkey://localhost:6379"
    SECRET_KEY: str = "should-be-changed"
    FAKE_DATA: bool = True


CONFIG_SETTINGS: ConfigSettings = ConfigSettings()
