from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from api.endpoints.models.v1.base import (
    AcapyItem,
    ListResponse,
)

from api.endpoints.routes.tenant_admin import TenantSchemaData


# use existing data format from v0, will need to be restructured here like contacts.
class SchemasListResponse(ListResponse[TenantSchemaData]):
    pass
