from fastapi.security import OAuth2PasswordBearer
from api.core.config import settings as s


class AuthTestStub:
    def __call__(self):
        return None


def check_oauth(tokenUrl: str):
    """
    Dependency function that yields OAuth2PasswordBearer if ENDPOINT_SECURITY_ENABLED
    """
    if not s.ENDPOINT_SECURITY_ENABLED:
        return AuthTestStub()
    return OAuth2PasswordBearer(tokenUrl=tokenUrl)
