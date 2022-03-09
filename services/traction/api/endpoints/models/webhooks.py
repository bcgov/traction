import re
from enum import Enum


class WebhookTopicType(str, Enum):
    ping = "ping"
    connections = "connections"
    oob_invitation = "oob-invitation"
    connection_reuse = "connection-reuse"
    connection_reuse_accepted = "connection-reuse-accepted"
    basicmessages = "basicmessages"
    issue_credential = "issue_credential"
    issue_credential_v2_0 = "issue-credential-v2-0"
    issue_credential_v2_0_indy = "issue-credential-v2-0-indy"
    issue_credential_v2_0_ld_proof = "issue-credential-v2-0-ld-proof"
    issuer_cred_rev = "issuer-cred-rev"
    present_proof = "present-proof"
    present_proof_v2_0 = "present-proof-v2-0"
    endorse_transaction = "endorse_transaction"
    revocation_registry = "revocation-registry"
    revocation_notification = "revocation-notification"
    problem_report = "problem-report"


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
WEBHOOK_ISSUE_LISTENER_PATTERN = re.compile(
    f"^{WEBHOOK_EVENT_PREFIX}{WebhookTopicType.issue_credential}(.*)?$"
)


class TenantEventTopicType(str, Enum):
    issuer = "issuer"
    schema = "schema"
    issue_cred = "issue_cred"


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
