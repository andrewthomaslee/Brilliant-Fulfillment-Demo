from fastapi import APIRouter
from .logs import router as logs_router
from .machines import router as machines_router
from .users import router as users_router


api_router: APIRouter = APIRouter(prefix="/api")
api_router.include_router(logs_router)
api_router.include_router(machines_router)
api_router.include_router(users_router)
