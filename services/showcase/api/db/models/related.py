from typing import List

from api.db.models.job_applicant import ApplicantRead
from api.db.models.out_of_band import OutOfBandRead
from api.db.models.sandbox import SandboxRead
from api.db.models.student import StudentRead
from api.db.models.line_of_business import LobRead


class SandboxReadPopulated(SandboxRead):
    lobs: List[LobRead] = None
    students: List[StudentRead] = None
    applicants: List[ApplicantRead] = None


class LobReadWithSandbox(LobRead):
    sandbox: SandboxRead = None


class OutOfBandReadPopulated(OutOfBandRead):
    sender: LobRead = None
    recipient: LobRead = None
