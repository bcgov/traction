from fastapi import APIRouter

from .presentation_requests import router as requests_router
from .presentation_request_templates import router as templates_router

router = APIRouter()
router.include_router(
    requests_router,
    prefix="/presentation-requests",
    tags=["presentation-requests"],
)
router.include_router(
    templates_router,
    prefix="/presentation-request-templates",
    tags=["presentation-requests", "templates"],
)
