from fastapi import APIRouter

from .contact import router as contact
from .contacts import router as contacts

router = APIRouter()
router.include_router(contacts)
router.include_router(contact)
