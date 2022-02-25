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
    proposal_received = "proposal-received"
    offer_sent = "offer-sent"
    request_received = "request-received"
    credential_issued = "credential-issued"
    # holder states
    proposal_sent = "proposal-sent"
    offer_received = "offer-received"
    request_sent = "request-sent"
    credential_received = "credential-received"
    # common states
    done = "done"
    abandoned = "abandoned"
    error = "error"


class AttributePreview(BaseSchema):
    name: str
    value: str

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class CredentialPreview(BaseSchema):
    attributes: list[AttributePreview]

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
