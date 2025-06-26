from fastapi import APIRouter
from app.config import settings
from app.api.v1.routers import router as v1_router


router = APIRouter(
    prefix=settings.api.v1.prefix,
)

router.include_router(
    v1_router,
    prefix=settings.api.v1.organizations
)