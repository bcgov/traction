# Import all the models, so that Base has them before being imported by Alembic

from api.db.models.base import TractionSQLModel  # noqa: F401
from api.db.models.student import Student

__all__ = ["TractionSQLModel", "Student"]
