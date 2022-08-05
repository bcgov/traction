from enum import Enum


class EndorserStateType(str, Enum):
    init = "init"
    request_received = "request_received"
    request_sent = "request_sent"
    transaction_acked = "transaction_acked"
    transaction_cancelled = "transaction_cancelled"
    transaction_created = "transaction_created"
    transaction_endorsed = "transaction_endorsed"
    transaction_refused = "transaction_refused"
    transaction_resent = "transaction_resent"
    transaction_resent_received = "transaction_resent_received"


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


class PTypeType(str, Enum):
    lt = "<"
    le = "<="
    ge = ">="
    gt = ">"
