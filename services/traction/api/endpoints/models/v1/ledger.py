from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from api.endpoints.models.v1.base import (
    AcapyItem,
    ListResponse,
)

from api.endpoints.routes.tenant_admin import TenantSchemaData


class CreateSchemaPayload(BaseModel):
    """CreateSchemaPayload.

    Payload for Create Schema as Traction Tenant with Issuer Permissions.

    Attributes:
      alias: required, must be unique. A name/label for the Contact
      invitation_type: what type of invitation to create

    """

    cred_def_id: UUID
    contact_id: UUID


# use existing data format from v0, will need to be restructured here like contacts.
class SchemasListResponse(ListResponse[TenantSchemaData]):
    pass
