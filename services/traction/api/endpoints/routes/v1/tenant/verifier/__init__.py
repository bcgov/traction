from fastapi import APIRouter

from .verifier_presentations import router as presentations_router
from .verifier_presentation import router as presentation_router
from .presentation_request_templates import router as templates_router
from .presentation_request_template import router as template_router


verifier_router = APIRouter()
verifier_router.include_router(presentations_router, prefix="/presentations", tags=[])
verifier_router.include_router(presentation_router, prefix="/presentations", tags=[])
verifier_router.include_router(
    templates_router, prefix="/presentation_templates", tags=[]
)
verifier_router.include_router(
    template_router, prefix="/presentation_templates", tags=[]
)
