from typing import List

from api.db.models.out_of_band import OutOfBandRead
from api.db.models.sandbox import SandboxRead
from api.db.models.student import StudentRead
from api.db.models.tenant import TenantRead


class SandboxReadPopulated(SandboxRead):
    tenants: List[TenantRead] = None
    students: List[StudentRead] = None


class TenantReadWithSandbox(TenantRead):
    sandbox: SandboxRead = None


class OutOfBandReadPopulated(OutOfBandRead):
    sender: TenantRead = None
    recipient: TenantRead = None
