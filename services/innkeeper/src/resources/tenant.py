import uuid

import requests
from flask import request
from flask_restful import Resource
from http import HTTPStatus

from marshmallow import ValidationError
from webargs import fields
from webargs.flaskparser import use_kwargs

from src.models import Tenant, AccessKey
from src.schemas.access_key import AccessKeyCreatedSchema, AccessKeyPaginationSchema
from src.schemas.tenant import TenantSchema, TenantPaginationSchema, TenantCreatedSchema
from src.utils import hash_password

from flask import current_app

resource_schema = TenantSchema()
resource_new_schema = TenantCreatedSchema()
resource_list_schema = TenantSchema(many=True)
resource_pagination_schema = TenantPaginationSchema()

access_key_new_schema = AccessKeyCreatedSchema()
access_key_pagination_schema = AccessKeyPaginationSchema()


class TenantListResource(Resource):
    @use_kwargs(
        {
            "q": fields.Str(missing=""),
            "page": fields.Int(missing=1),
            "per_page": fields.Int(missing=20),
            "sort": fields.Str(missing="created_at"),
            "order": fields.Str(missing="desc"),
        }
    )
    def get(self, q, page, per_page, sort, order):

        if sort not in ["created_at", "name"]:
            sort = "created_at"

        if order not in ["asc", "desc"]:
            order = "desc"

        paginated_items = Tenant.get_all_active(q, page, per_page, sort, order)

        return resource_pagination_schema.dump(paginated_items), HTTPStatus.OK

    def post(self):

        json_data = request.get_json()

        data = resource_schema.load(data=json_data)
        try:
            data = resource_schema.load(data=json_data)
        except ValidationError as err:
            return {
                "message": "Validation errors",
                "errors": err.messages,
            }, HTTPStatus.BAD_REQUEST

        tenant = Tenant(**data)
        if not Tenant.get_by_name(tenant.name):

            # create a tenant in acapy - move to service
            url = f"{current_app.config['ACAPY_ADMIN_URL']}/multitenancy/wallet"
            headers = {"accept": "application/json", "Content-Type": "application/json"}
            data = {
                "label": tenant.name,
                "wallet_key": str(uuid.uuid4()),
                "wallet_name": str(uuid.uuid4()),
            }
            response = requests.post(url=url, json=data, headers=headers)
            if response.status_code == HTTPStatus.OK:
                acapy_tenant = response.json()
                # create an access key
                tenant_password = str(uuid.uuid4())
                tenant_access_key = AccessKey(
                    password=hash_password(tenant_password), is_active=True
                )
                tenant.access_keys.append(tenant_access_key)
                tenant.wallet_id = acapy_tenant["wallet_id"]
                tenant.is_active = True
                tenant.save()

                result = resource_new_schema.dump(tenant)
                result["access_key"] = tenant_password
                return result, HTTPStatus.CREATED
            else:
                return {
                    "message": "Error creating tenant",
                    "errors": response.text,
                }, HTTPStatus.BAD_REQUEST
        else:
            return resource_schema.dump(tenant), HTTPStatus.CONFLICT


class TenantResource(Resource):
    def get(self, tenant_id):

        item = Tenant.get_by_id(id=tenant_id)

        if item is None:
            return {"message": "Tenant not found"}, HTTPStatus.NOT_FOUND

        return resource_schema.dump(item), HTTPStatus.OK


class TenantAccessKeyListResource(Resource):
    @use_kwargs({"page": fields.Int(missing=1), "per_page": fields.Int(missing=10)})
    def get(self, tenant_id, page, per_page):

        tenant = Tenant.get_by_id(tenant_id)
        if tenant is None:
            return {"message": "Tenant not found"}, HTTPStatus.NOT_FOUND

        paginated_recipes = AccessKey.get_all_by_tenant(
            tenant_id=tenant.id, page=page, per_page=per_page
        )

        return access_key_pagination_schema.dump(paginated_recipes), HTTPStatus.OK

    def post(self, tenant_id):

        tenant = Tenant.get_by_id(tenant_id)
        if tenant is None:
            return {"message": "Tenant not found"}, HTTPStatus.NOT_FOUND

        # generate and add a new access key for this tenant
        tenant_password = str(uuid.uuid4())
        tenant_access_key = AccessKey(
            password=hash_password(tenant_password),
            is_active=tenant.is_active,
            tenant_id=tenant.id,
        )
        tenant_access_key.save()

        # for the return, we want to show the unencrypted password...
        return (
            access_key_new_schema.dump({"access_key": tenant_password}),
            HTTPStatus.OK,
        )
