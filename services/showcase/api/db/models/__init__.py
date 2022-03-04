# Import all the models, so that Base has them before being imported by Alembic

from api.db.models.base import BaseTable  # noqa: F401
from api.db.models.out_of_band import OutOfBand
from api.db.models.student import Student
from api.db.models.sandbox import Sandbox
from api.db.models.line_of_business import Lob
from api.db.models.job_applicant import Applicant

__all__ = ["BaseTable", "OutOfBand", "Student", "Sandbox", "Lob", "Applicant"]
