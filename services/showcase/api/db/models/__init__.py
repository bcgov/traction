# Import all the models, so that Base has them before being imported by Alembic

from api.db.models.base import BaseTable  # noqa: F401
from api.db.models.student import Student
from api.db.models.sandbox import Sandbox
from api.db.models.tenant import Tenant

__all__ = ["BaseTable", "Student", "Sandbox", "Tenant"]
