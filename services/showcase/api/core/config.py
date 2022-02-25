import logging
import os
from enum import Enum
from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, PostgresDsn

logger = logging.getLogger(__name__)


class EnvironmentEnum(str, Enum):
    PRODUCTION = "production"
    LOCAL = "local"


class GlobalConfig(BaseSettings):
    TITLE: str = "Traction Showcase"
    DESCRIPTION: str = "A Showcase app for Traction"

    ENVIRONMENT: EnvironmentEnum
    DEBUG: bool = False
    TESTING: bool = False
    TIMEZONE: str = "UTC"

    # the following defaults match up with default values in scripts/.env.example
    # these MUST be all set in non-local environments.
    PSQL_HOST: str = os.environ.get("POSTGRESQL_HOST", "localhost")
    PSQL_PORT: int = os.environ.get("POSTGRESQL_PORT", 6543)
    PSQL_DB: str = os.environ.get("POSTGRESQL_DB", "showcase")

    PSQL_USER: str = os.environ.get("SHOWCASE_DB_USER", "showcaseuser")
    PSQL_PASS: str = os.environ.get("SHOWCASE_DB_USER_PWD", "showcasePass")

    PSQL_ADMIN_USER: str = os.environ.get("SHOWCASE_DB_ADMIN", "showcaseadminuser")
    PSQL_ADMIN_PASS: str = os.environ.get("SHOWCASE_DB_ADMIN_PWD", "showcaseadminPass")

    # application connection is async
    # fmt: off
    SQLALCHEMY_DATABASE_URI: PostgresDsn = (
        f"postgresql+asyncpg://{PSQL_USER}:{PSQL_PASS}@{PSQL_HOST}:{PSQL_PORT}/{PSQL_DB}"  # noqa: E501
    )
    # migrations connection uses owner role and is synchronous
    SQLALCHEMY_DATABASE_ADMIN_URI: PostgresDsn = (
        f"postgresql://{PSQL_ADMIN_USER}:{PSQL_ADMIN_PASS}@{PSQL_HOST}:{PSQL_PORT}/{PSQL_DB}"  # noqa: E501
    )
    # fmt: on

    TRACTION_ENDPOINT: str = os.environ.get(
        "TRACTION_ENDPOINT", "http://host.docker.internal:5100"
    )
    TRACTION_API_ADMIN_USER: str = os.environ.get(
        "TRACTION_API_ADMIN_USER", "innkeeper"
    )
    TRACTION_API_ADMIN_KEY: str = os.environ.get("TRACTION_API_ADMIN_KEY", "change-me")
    TRACTION_WEBHOOK_URL_API_KEY_NAME = "x-api-key"

    SHOWCASE_ENDPOINT: str = os.environ.get(
        "SHOWCASE_ENDPOINT", "http://host.docker.internal:5200"
    )

    SHOWCASE_STATIC_FILES: str = os.environ.get(
        "SHOWCASE_STATIC_FILES", "/traction/static"
    )

    SHOWCASE_CORS_URLS: str = os.environ.get("SHOWCASE_CORS_URLS", "")

    # Api V1 prefix
    API_V1_STR = "/v1"

    DB_ECHO_LOG: bool = False

    class Config:
        case_sensitive = True


class LocalConfig(GlobalConfig):
    """Local configurations."""

    DEBUG: bool = True
    ENVIRONMENT: EnvironmentEnum = EnvironmentEnum.LOCAL
    SHOWCASE_STATIC_FILES = "../frontend/dist"


class ProdConfig(GlobalConfig):
    """Production configurations."""

    DEBUG: bool = False
    ENVIRONMENT: EnvironmentEnum = EnvironmentEnum.PRODUCTION


class FactoryConfig:
    def __init__(self, environment: Optional[str]):
        self.environment = environment

    def __call__(self) -> GlobalConfig:
        if self.environment == EnvironmentEnum.LOCAL.value:
            return LocalConfig()
        return ProdConfig()


@lru_cache()
def get_configuration() -> GlobalConfig:
    return FactoryConfig(os.environ.get("ENVIRONMENT"))()


settings = get_configuration()
