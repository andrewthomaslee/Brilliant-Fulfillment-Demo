from pathlib import Path

BASE_DIR: Path = Path(__file__).parent
DATA_DIR: Path = Path(BASE_DIR.parent / "data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL: str = f"sqlite:///{DATA_DIR / 'sqlite.db'}"
