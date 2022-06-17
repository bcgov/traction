from fastapi import APIRouter

from .verification_requests import router as presentation_router

verifier_router = APIRouter()
verifier_router.include_router(
    presentation_router, prefix="/presentation_requests", tags=[]
)
