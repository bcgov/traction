from marshmallow import Schema, fields, validate

from src.schemas.pagination import PaginationSchema


class TenantSchema(Schema):
    class Meta:
        ordered = True

    id = fields.UUID(dump_only=True)
    name = fields.String(required=True, validate=[validate.Length(max=80)])
    wallet_id = fields.UUID(dump_only=True)
    is_active = fields.Boolean()

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class TenantPaginationSchema(PaginationSchema):
    data = fields.Nested(TenantSchema, attribute="items", many=True)


class TenantCreatedSchema(TenantSchema):
    access_key = fields.String()
