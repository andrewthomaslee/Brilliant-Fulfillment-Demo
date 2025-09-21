from fastapi import APIRouter
from .admin import router as admin_router


router: APIRouter = APIRouter(
    prefix="/",
)
router.include_router(admin_router)
