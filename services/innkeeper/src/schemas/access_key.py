from marshmallow import Schema, fields

from src.schemas.pagination import PaginationSchema


class AccessKeySchema(Schema):
    class Meta:
        ordered = True

    id = fields.UUID(dump_only=True)
    is_admin = fields.Boolean(dump_only=True)
    is_active = fields.Boolean(dump_only=True)

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    tenant_id = fields.UUID()


class AccessKeyPaginationSchema(PaginationSchema):
    data = fields.Nested(AccessKeySchema, attribute="items", many=True)


class AccessKeyCreatedSchema(Schema):
    access_key = fields.String()
