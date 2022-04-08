from fastapi import APIRouter

from .presentation_requests import router as requests
from .presentation_request_templates import router as templates

router = APIRouter()
router.include_router(
    requests,
    prefix="/presentation-requests",
    tags=["presentation-requests"],
)
router.include_router(
    templates,
    prefix="/presentation-request-templates",
    tags=["presentation-requests", "templates"],
)
