from enum import Enum


class HolderCredentialStatusType(str, Enum):
    # pending, nothing happened yet
    pending = "Pending"
    # offer received, waiting for action
    offer_received = "Offer Received"
    # offer received, action taken to accept, not in wallet
    offer_accepted = "Offer Accepted"
    # credential in holder's wallet
    accepted = "Accepted"
    # credential offer was rejected
    rejected = "Rejected"
    # this has been revoked by the issuer
    revoked = "Revoked"
    # item is soft deleted
    deleted = "Delete"
    error = "Error"
