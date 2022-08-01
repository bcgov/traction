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
