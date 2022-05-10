from typing import Optional

from pydantic import BaseModel

from api.endpoints.models.v1.base import (
    ListResponse,
)

from api.endpoints.routes.tenant_admin import TenantSchemaRead
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
    cred_def_tag: Optional[str]
    revocable: bool | None = False
    revoc_reg_size: int | None = 1000


class ImportSchemaPayload(BaseModel):
    """ImportSchemaPayload.

    Payload for Create Schema as Traction Tenant with Issuer Permissions.

    Attributes:
      schema_id:
      cred_def_tag:
      revocable:
    """

    # using existing schema_request shape from v0
    schema_id: str
    cred_def_tag: Optional[str]
    revocable: bool | None = False
    revoc_reg_size: int | None = 1000


# use existing data format from v0, will need to be restructured here like contacts.
class SchemasListResponse(ListResponse[TenantSchemaRead]):
    pass
