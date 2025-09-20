#!/usr/bin/env python

if __name__ == "__main__":
    import subprocess
    from pathlib import Path
    import uvicorn

    BASE_DIR: Path = Path(__file__).parent
    # Valkey setup
    Path(BASE_DIR / "data").mkdir(parents=True, exist_ok=True)
    subprocess.run(["valkey-server"], cwd=BASE_DIR / "data", check=True)

    # Database setup

    # FastAPI start
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=7999,
        workers=3,
        timeout_graceful_shutdown=10,
        use_colors=True,
    )
