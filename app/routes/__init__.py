from fastapi import APIRouter
from .admin import router as admin_router


router: APIRouter = APIRouter(prefix="/api")
router.include_router(admin_router)
