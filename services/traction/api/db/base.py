# Import all the models, so that Base has them before being imported by Alembic

from api.db.base_class import Base  # noqa: F401
from api.db.tables.tenants import Tenant  # noqa: F401
from api.db.tables.access_keys import AccessKey  # noqa: F401
