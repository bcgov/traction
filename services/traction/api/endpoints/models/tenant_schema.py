from api.db.models.base import BaseSchema


class TenantSchemaRequest(BaseSchema):
    schema_name: str
    schema_version: str
    attributes: list[str]
