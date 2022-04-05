import logging
import os
from enum import Enum
from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, PostgresDsn

from api.core.event_bus import EventBus


logger = logging.getLogger(__name__)


class EnvironmentEnum(str, Enum):
    PRODUCTION = "production"
    LOCAL = "local"


class GlobalConfig(BaseSettings):
    TITLE: str = "Traction"
    DESCRIPTION: str = "A digital wallet solution for organizations"

    # sub-app titles/descriptions
    TENANT_TITLE: str = "Traction Tenant"
    TENANT_DESCRIPTION: str = "Endpoints for Tenants of Traction"

    INNKEEPER_TITLE: str = "Traction Innkeeper"
    INNKEEPER_DESCRIPTION: str = "Endpoints for Innkeeper of Traction"

    ENVIRONMENT: EnvironmentEnum
    DEBUG: bool = False
    TESTING: bool = False
    TIMEZONE: str = "UTC"

    # the following defaults match up with default values in scripts/.env.example
    # these MUST be all set in non-local environments.
    PSQL_HOST: str = os.environ.get("POSTGRESQL_HOST", "localhost")
    PSQL_PORT: int = os.environ.get("POSTGRESQL_PORT", 5432)
    PSQL_DB: str = os.environ.get("POSTGRESQL_DB", "traction")

    PSQL_USER: str = os.environ.get("TRACTION_DB_USER", "tractionuser")
    PSQL_PASS: str = os.environ.get("TRACTION_DB_USER_PWD", "tractionPass")

    PSQL_ADMIN_USER: str = os.environ.get("TRACTION_DB_ADMIN", "tractionadminuser")
    PSQL_ADMIN_PASS: str = os.environ.get("TRACTION_DB_ADMIN_PWD", "tractionadminPass")

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

    ACAPY_ADMIN_URL: str = os.environ.get("ACAPY_ADMIN_URL", "http://localhost:8031")
    ACAPY_ADMIN_URL_API_KEY: str = os.environ.get(
        "ACAPY_ADMIN_URL_API_KEY", "change-me"
    )

    TRACTION_API_ADMIN_USER: str = os.environ.get(
        "TRACTION_API_ADMIN_USER", "innkeeper"
    )
    TRACTION_API_ADMIN_KEY: str = os.environ.get("TRACTION_API_ADMIN_KEY", "change-me")

    TRACTION_WEBHOOK_URL: str = os.environ.get(
        "TRACTION_WEBHOOK_URL", "http://traction-api:5000/webhook"
    )
    TRACTION_TENANT_WEBHOOK_URL: str = os.environ.get(
        "TRACTION_TENANT_WEBHOOK_URL", "http://traction-api:5000/webhook/tenant"
    )
    ACAPY_WEBHOOK_URL_API_KEY_NAME = "x-api-key"
    ACAPY_WEBHOOK_URL_API_KEY: str = os.environ.get("ACAPY_WEBHOOK_URL_API_KEY", "")

    ACAPY_ENDORSER_PUBLIC_DID: str = os.environ.get("ACAPY_ENDORSER_PUBLIC_DID")
    ENDORSER_CONNECTION_ALIAS: str = os.environ.get(
        "ENDORSER_CONNECTION_ALIAS", "endorser"
    )

    ACAPY_GENESIS_URL: str = os.environ.get("ACAPY_GENESIS_URL")

    DB_ECHO_LOG: bool = False

    # Api V1 prefix
    API_V0_STR = "/v0"
    API_V1_STR = "/v1"

    # openssl rand -hex 32
    JWT_SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 300

    EVENT_BUS: EventBus = EventBus()

    class Config:
        case_sensitive = True


class LocalConfig(GlobalConfig):
    """Local configurations."""

    DEBUG: bool = True
    ENVIRONMENT: EnvironmentEnum = EnvironmentEnum.LOCAL


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
