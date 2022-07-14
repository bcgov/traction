from enum import Enum
import json
from typing import Dict

from api.db.models.base import BaseSchema


class IssueCredentialProtocolType(str, Enum):
    v10 = "v1.0"
    v20 = "v2.0"


class CredentialType(str, Enum):
    anoncreds = "anoncreds"
    json_ld = "json_ld"


class CredentialRoleType(str, Enum):
    issuer = "issuer"
    holder = "holder"


class CredentialStateType(str, Enum):
    # issuer states
    pending = "pending"
    proposal_received = "proposal_received"
    offer_sent = "offer_sent"
    request_received = "request_received"
    credential_issued = "credential_issued"
    # holder states
    proposal_sent = "proposal_sent"
    offer_received = "offer_received"
    request_sent = "request_sent"
    credential_received = "credential_received"
    # common states
    credential_acked = "credential_acked"
    done = "done"
    abandoned = "abandoned"
    error = "error"
    credential_revoked = "credential_revoked"


class PresentCredentialProtocolType(str, Enum):
    v10 = "v1.0"
    v20 = "v2.0"


class PresentationRoleType(str, Enum):
    verifier = "verifier"
    holder = "holder"
    prover = "prover"


class PresentationStateType(str, Enum):
    # verifier states
    pending = "pending"
    proposal_received = "proposal_received"
    request_sent = "request_sent"
    presentation_received = "presentation_received"
    verified = "verified"
    # holder states
    proposal_sent = "proposal_sent"
    request_received = "request_received"
    presentation_sent = "presentation_sent"
    reject_sent = "reject_sent"
    # common states
    presentation_acked = "presentation_acked"
    done = "done"
    abandoned = "abandoned"
    error = "error"


class AttributePreview(BaseSchema):
    name: str
    value: str

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)


class CredentialPreview(BaseSchema):
    attributes: list[AttributePreview]

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)


class ProofReqAttr(BaseSchema):
    name: str | None = None
    names: list[str] | None = None
    non_revoked: dict | None = None
    restrictions: list[dict] | None = None

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)


class PTypeType(str, Enum):
    lt = "<"
    le = "<="
    ge = ">="
    gt = ">"


class ProofReqPred(BaseSchema):
    name: str
    p_type: PTypeType
    p_value: int
    non_revoked: dict | None = None
    restrictions: list[dict]

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)


class ProofRequest(BaseSchema):
    requested_attributes: list[ProofReqAttr]
    requested_predicates: list[ProofReqPred]
    non_revoked: dict | None = None

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)


class CredPrecisForProof(BaseSchema):
    cred_info: dict
    interval: dict | None = None
    presentation_referents: list


class PresentationAttribute(BaseSchema):
    cred_id: str
    revealed: bool

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)


class PresentationPredicate(BaseSchema):
    cred_id: str
    timestamp: int | None = None

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)


class CredPresentation(BaseSchema):
    requested_attributes: Dict[str, PresentationAttribute]
    requested_predicates: Dict[str, PresentationPredicate]
    self_attested_attributes: dict

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)
