from datetime import datetime, timedelta

from jose import jwt
from pydantic import BaseModel

from api.core.config import settings


class AccessToken(BaseModel):
    access_token: str
    token_type: str


def create_access_token(data: dict):
    expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return AccessToken(access_token=encoded_jwt, token_type="bearer")
