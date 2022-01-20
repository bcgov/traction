from fastapi import APIRouter
from typing import Optional

router = APIRouter()

@router.get("/")
def get_all_tenants(): 
    pass

