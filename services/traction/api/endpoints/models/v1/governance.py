import uuid
from enum import Enum
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel

from api.endpoints.models.v1.base import (
    ListResponse,
    TagsItem,
    GetResponse,
    ListTagsItemParameters,
)

from api.endpoints.routes.tenant_admin import TenantSchemaRead
from api.endpoints.models.tenant_schema import TenantSchemaRequest
from api.protocols.v1.endorser.endorser_protocol import EndorserStateType


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


class TemplateStatusType(str, Enum):
    active = "Active"
    in_progress = "In Progress"
    pending = "Pending"
    deleted = "Deleted"
    cancelled = "Cancelled"
    error = "Error"


class SchemaTemplateListParameters(
    ListTagsItemParameters[TemplateStatusType, EndorserStateType]
):
    """SchemaTemplateListParameters.

    Inherits from ListTagsItemParameters.
    Filters for fetching SchemaTemplateItem

    Attributes:
      name: return SchemaTemplateItem like name

    """

    name: str | None = None
    schema_id: str | None = None
    schema_template_id: uuid.UUID | None = None


class CredentialTemplateListParameters(
    ListTagsItemParameters[TemplateStatusType, EndorserStateType]
):
    """CredentialTemplateListParameters.

    Inherits from ListTagsItemParameters.
    Filters for fetching CredentialTemplateItem

    Attributes:
      name: return CredentialTemplateItem like name

    """

    name: str | None = None
    cred_def_id: str | None = None
    credential_template_id: uuid.UUID | None = None
    schema_id: str | None = None
    schema_template_id: uuid.UUID | None = None


class SchemaTemplateItem(TagsItem[TemplateStatusType, EndorserStateType]):
    """SchemaTemplateItem.

    Inherits from Item.
    Representation for the SchemaTemplate database record.

    Attributes:
      schema_template_id: Traction ID for the schema template
      schema_id: This will be the ledger schema id - this is not a UUID
      tenant_id: Traction Tenant ID, owner of this Contact
      name: a "pretty" name for the schema, this can be different than the name on the
        ledger (schema_name).
      status: current state of the Schema - Pending, In Progress, Completed, Deleted
      tags: Set by tenant for arbitrary grouping of their Schemas
      deleted: Schema/Tenant "soft" delete indicator.
      imported: When True, this tenant imported the schema, otherwise they created it
      version: version, on ledger
      attributes: list of attribute names, on ledger

    """

    schema_template_id: uuid.UUID
    tenant_id: UUID
    schema_id: str | None = None
    name: str
    imported: bool

    # ledger data ---
    schema_name: str
    version: str
    attributes: List[str] | None = []


class CredentialTemplateItem(TagsItem[TemplateStatusType, EndorserStateType]):
    """CredentialTemplateItem.

    Inherits from Item.
    Representation for the CredentialTemplate database record.

    Attributes:
      credential_template_id: Traction ID for the credential template
      schema_template_id: Traction ID for the parent schema template
      schema_id: This will be the ledger schema id - this is not a UUID
      cred_def_id: This will be the ledger cred def id - this is not a UUID
      tenant_id: Traction Tenant ID, owner of this Contact
      name: a "pretty" name for the item, this can be different than the name on the
        ledger (schema_name).
      status: current state of the item - Pending, In Progress, Completed, Deleted
      tags: Set by tenant for arbitrary grouping of their credential templates
      deleted: Schema/Tenant "soft" delete indicator.
      revocation_enabled: whether this template/cred def can be revoked.
      attributes: list of attribute names, on ledger

    """

    schema_template_id: uuid.UUID
    credential_template_id: uuid.UUID
    tenant_id: UUID
    schema_id: str | None = None
    cred_def_id: str | None = None
    name: str
    revocation_enabled: bool

    # ledger data ---
    attributes: List[str] | None = []
    tag: str | None = None


class SchemaTemplateListResponse(ListResponse[SchemaTemplateItem]):
    pass


class CredentialTemplateListResponse(ListResponse[CredentialTemplateItem]):
    pass


class SchemaDefinitionPayload(BaseModel):
    schema_name: str
    schema_version: str
    attributes: List[str]


class CredentialDefinitionPayload(BaseModel):
    tag: str
    revocation_enabled: bool = False
    revocation_registry_size: int = 0


class SchemaTemplateGetResponse(GetResponse[SchemaTemplateItem]):
    pass


class CredentialTemplateGetResponse(GetResponse[CredentialTemplateItem]):
    pass


class CreateSchemaTemplatePayload(BaseModel):
    """CreateSchemaTemplatePayload.

    Payload for Create Schema (Template) as Traction Tenant with Issuer Permissions.
    This will create a new Schema on the ledger, associate with this Tenant.

    Optionally, create a Credential Definition for this Schema/Tenant.

    Attributes:
      schema_definition: (required) The schema definition to write to the ledger.
      name: (optional) Traction name, if None, will use schema.schema_name
      tags: (optional) list of strings to categorize the schema in Traction
      credential_definition: (optional) if specified, create a Credential Definition
    """

    schema_definition: SchemaDefinitionPayload
    name: Optional[str] | None = None
    tags: Optional[List[str]] | None = []
    credential_definition: Optional[CredentialDefinitionPayload] | None = None


class CreateSchemaTemplateResponse(SchemaTemplateGetResponse):
    """CreateSchemaTempalateResponse.

    Response to Create Schema (Template) API.

    Attributes:

    """

    credential_template: CredentialTemplateItem | None = None


class CreateCredentialTemplatePayload(BaseModel):
    """CreateCredentialTemplatePayload.

    Payload for Create Credential (Template) as Traction Tenant with Issuer Permissions.
    This will create a new Credential Definition on the ledger, associate with this
    Tenant and a Schema.

    Either schema_id (ledger id) or schema_template_id (Traction ID) is required. If
    schema_id is used AND that schema does not have an existing Schema Template, then it
     will be imported and Schema Template will be created.

    Attributes:
      credential_definition: (required) create a Credential Definition
      schema_id: (required if no schema_template_id), Ledger ID of schema
      schema_template_id: (required if no schema_id), Traction ID of schema template
      name: (required) Traction name
      tags: (optional) list of strings to categorize the credential template in Traction
    """

    credential_definition: CredentialDefinitionPayload
    schema_id: str | None = None
    schema_template_id: UUID | None = None
    name: str
    tags: Optional[List[str]] | None = []


class CreateCredentialTemplateResponse(CredentialTemplateGetResponse):
    """CreateCredentialTemplateResponse.

    Response to Create Credential (Template) API.

    Attributes:

    """

    pass


class ImportSchemaTemplatePayload(BaseModel):
    """ImportSchemaTemplatePayload.

    Payload for Import Schema (Template) as Traction Tenant with Issuer Permissions.
    This will import data about the schema from the ledger to Traction

    Optionally, create a Credential Definition for this Schema/Tenant.

    Attributes:
      schema_id: (required) The schema id on the ledger.
      name: (optional) Traction name, if None, will use schema.schema_name
      tags: (optional) list of strings to categorize the schema in Traction
      credential_definition: (optional) if specified, create a Credential Definition
    """

    schema_id: str
    name: Optional[str] | None = None
    tags: Optional[List[str]] | None = []
    credential_definition: Optional[CredentialDefinitionPayload] | None = None


class ImportSchemaTemplateResponse(GetResponse[SchemaTemplateItem]):
    """ImportSchemaTemplateResponse.

    Response to Import Schema (Template) API.

    Attributes:

    """

    credential_template: CredentialTemplateItem | None = None


class UpdateSchemaTemplatePayload(BaseModel):
    """UpdateSchemaTemplatePayload.

    Payload for SchemaTemplate API update.
    Additional fields may be in the payload, but they will be ignored. Only these fields
     will be updated.


    Attributes:
      schema_template_id: Traction SchemaTemplate ID, item we are updating.
      status: update Status to this value
      name: update the Traction name
      tags: list of tags will be replaced with this list
    """

    schema_template_id: UUID
    name: str | None = None
    status: TemplateStatusType | None = None
    tags: List[str] | None = []


class UpdateSchemaTemplateResponse(GetResponse[SchemaTemplateItem]):
    pass


class UpdateCredentialTemplatePayload(BaseModel):
    """UpdateCredentialTemplatePayload.

    Payload for CredentialTemplate API update.
    Additional fields may be in the payload, but they will be ignored. Only these fields
     will be updated.


    Attributes:
      credential_template_id: Traction CredentialTemplate ID, item we are updating.
      status: update Status to this value
      name: update the Traction name
      tags: list of tags will be replaced with this list
    """

    credential_template_id: UUID
    name: str | None = None
    status: TemplateStatusType | None = None
    tags: List[str] | None = []


class UpdateCredentialTemplateResponse(GetResponse[CredentialTemplateItem]):
    pass
