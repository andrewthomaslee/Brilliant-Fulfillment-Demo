#!/usr/bin/env python

if __name__ == "__main__":
    import subprocess
    from pathlib import Path
    import uvicorn
    import valkey
    from time import sleep
    import logging
    from logging import Logger
    import os
    from dotenv import load_dotenv

    # My Imports
    from app.db import create_database

    # Logging setup
    logging.basicConfig(level=logging.INFO)
    logger: Logger = logging.getLogger(__name__)
    BASE_DIR: Path = Path(__file__).parent
    DATA_DIR: Path = Path(".." / BASE_DIR / "data")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    load_dotenv(Path(BASE_DIR.parent / ".env"))

    # Valkey setup
    subprocess.Popen(["valkey-server"], cwd=DATA_DIR)
    r = valkey.Valkey()
    while True:
        try:
            if r.ping():
                logger.info("Valkey is ready.")
                del r
                break
        except valkey.exceptions.ConnectionError:
            pass
        logger.info("Waiting for Valkey to start...")
        sleep(1)

    # DuckDB setup
    DUCK_DB = str(DATA_DIR / "duck.db")
    logger.info(f"Init DuckDB database: {DUCK_DB}")
    create_database(DUCK_DB)
    logger.info("DuckDB database created.")

    # FastAPI start
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=7999,
        workers=3,
        timeout_graceful_shutdown=10,
        use_colors=True,
    )
