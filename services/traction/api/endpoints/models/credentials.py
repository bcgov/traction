from enum import Enum
import json

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


class AttributePreview(BaseSchema):
    name: str
    value: str

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)


class CredentialPreview(BaseSchema):
    attributes: list[AttributePreview]

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)
