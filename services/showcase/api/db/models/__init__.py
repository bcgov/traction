# Import all the models, so that Base has them before being imported by Alembic

from api.db.models.base import BaseTable  # noqa: F401
from api.db.models.student import Student
from api.db.models.sandbox import Sandbox, Tenant

__all__ = ["BaseTable", "Student", "Sandbox", "Tenant"]
