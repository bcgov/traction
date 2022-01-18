from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api

from config import Config
from extensions import db
from src.resources.tenant import (
    TenantListResource,
    TenantResource,
    TenantAccessKeyListResource,
)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    register_extensions(app)
    register_resources(app)

    return app


def register_extensions(app):
    db.init_app(app)
    Migrate(app, db)


def register_resources(app):
    api = Api(app)
    api.add_resource(TenantListResource, "/tenants")
    api.add_resource(TenantResource, "/tenants/<uuid:tenant_id>")
    api.add_resource(TenantAccessKeyListResource, "/tenants/<uuid:tenant_id>/keys")


if __name__ == "__main__":
    app = create_app()
    app.run()
