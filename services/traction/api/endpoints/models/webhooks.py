import re
from enum import Enum


class WebhookTopicType(str, Enum):
    ping = "ping"
    connections = "connections"
    oob_invitation = "oob_invitation"
    connection_reuse = "connection_reuse"
    connection_reuse_accepted = "connection_reuse_accepted"
    basicmessages = "basicmessages"
    issue_credential = "issue_credential"
    issue_credential_v2_0 = "issue_credential_v2_0"
    issue_credential_v2_0_indy = "issue_credential_v2_0_indy"
    issue_credential_v2_0_ld_proof = "issue_credential_v2_0_ld_proof"
    issuer_cred_rev = "issuer_cred_rev"
    present_proof = "present_proof"
    present_proof_v2_0 = "present_proof_v2_0"
    endorse_transaction = "endorse_transaction"
    revocation_registry = "revocation_registry"
    revocation_notification = "revocation_notification"
    problem_report = "problem_report"


# the event id will be "acapy::WEBHOOK::<topic>::<potentially some other id>"
# ... and the event payload should contain the webhook payload
WEBHOOK_EVENT_PREFIX = "acapy::WEBHOOK::"
WEBHOOK_LISTENER_PATTERN = re.compile(f"^{WEBHOOK_EVENT_PREFIX}(.*)?$")
WEBHOOK_PING_LISTENER_PATTERN = re.compile(
    f"^{WEBHOOK_EVENT_PREFIX}{WebhookTopicType.ping}(.*)?$"
)
WEBHOOK_CONNECTIONS_LISTENER_PATTERN = re.compile(
    f"^{WEBHOOK_EVENT_PREFIX}{WebhookTopicType.connections}(.*)?$"
)
WEBHOOK_BASICMESSAGES_LISTENER_PATTERN = re.compile(
    f"^{WEBHOOK_EVENT_PREFIX}{WebhookTopicType.basicmessages}(.*)?$"
)
WEBHOOK_ENDORSE_LISTENER_PATTERN = re.compile(
    f"^{WEBHOOK_EVENT_PREFIX}{WebhookTopicType.endorse_transaction}(.*)?$"
)
WEBHOOK_PROBLEM_REPORT_LISTENER_PATTERN = re.compile(
    f"^{WEBHOOK_EVENT_PREFIX}{WebhookTopicType.problem_report}(.*)?$"
)
WEBHOOK_ISSUE_LISTENER_PATTERN = re.compile(
    f"^{WEBHOOK_EVENT_PREFIX}{WebhookTopicType.issue_credential}(.*)?$"
)
WEBHOOK_PRESENT_LISTENER_PATTERN = re.compile(
    f"^{WEBHOOK_EVENT_PREFIX}{WebhookTopicType.present_proof}(.*)?$"
)


class TenantEventTopicType(str, Enum):
    issuer = "issuer"
    schema = "schema"
    issue_cred = "issue_cred"
    present_req = "present_req"


# the event id will be "traction::EVENT::<topic>::<potentially some other id>"
# this is for handling and publishing non-acapy events to tenants via webhooks
#
TRACTION_EVENT_PREFIX = "traction::EVENT::"
TRACTION_EVENT_LISTENER_PATTERN = re.compile(f"^{TRACTION_EVENT_PREFIX}(.*)?$")
TRACTION_ISSUER_LISTENER_PATTERN = re.compile(
    f"^{TRACTION_EVENT_PREFIX}{TenantEventTopicType.issuer}(.*)?$"
)
TRACTION_SCHEMA_LISTENER_PATTERN = re.compile(
    f"^{TRACTION_EVENT_PREFIX}{TenantEventTopicType.schema}(.*)?$"
)
