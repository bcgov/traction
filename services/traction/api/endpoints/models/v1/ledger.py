from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from api.endpoints.models.v1.base import (
    ListResponse,
)

from api.endpoints.routes.tenant_admin import TenantSchemaData
from api.endpoints.models.tenant_schema import TenantSchemaRequest


class CreateSchemaPayload(BaseModel):
    """CreateSchemaPayload.

    Payload for Create Schema as Traction Tenant with Issuer Permissions.

    Attributes:
      schema_request: required
      schema_id:
      cred_def_tag:
      revocable:
    """

    # using existing schema_request shape from v0
    schema_request: TenantSchemaRequest | None = None
    schema_id: Optional[UUID]
    cred_def_tag: Optional[str]
    revocable: bool | None = False
    revoc_reg_size: int | None = 1000


# use existing data format from v0, will need to be restructured here like contacts.
class SchemasListResponse(ListResponse[TenantSchemaData]):
    pass
