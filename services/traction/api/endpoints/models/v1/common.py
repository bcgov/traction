import json
from typing import Dict

from pydantic import BaseModel

from api.db.models.base import BaseSchema
from api.endpoints.models.v1.enumerated import PTypeType


class CommentPayload(BaseModel):
    comment: str


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
