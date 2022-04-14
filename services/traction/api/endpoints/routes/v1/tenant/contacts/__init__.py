from fastapi import APIRouter

from .contact import router as contact
from .contacts import router as contacts

contacts_router = APIRouter()
contacts_router.include_router(contacts, tags=[])
contacts_router.include_router(contact, tags=[])
