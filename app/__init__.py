from fastapi import APIRouter
# pyrefly: ignore  # import-error
from .bff import bff_router

router: APIRouter = APIRouter()

router.include_router(bff_router)


def hello() -> None:
    print("Hello from monotes!\n❄️🐍💨")
