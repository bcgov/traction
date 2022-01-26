# Import all the models, so that Base has them before being imported by Alembic

from api.db.models.base import TractionSQLModel  # noqa: F401
from api.db.models.tenant import Tenant  # noqa: F401

__all__ = ["TractionSQLModel", "Tenant"]
