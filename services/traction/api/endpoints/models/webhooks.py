import re


# the event id will be "traction::WEBHOOK::<topic>::<potentially some other id>"
# ... and the event payload should contain the webhook payload
WEBHOOK_EVENT_PREFIX = "traction::WEBHOOK::"
WEBHOOK_LISTENER_PATTERN = re.compile(f"^{WEBHOOK_EVENT_PREFIX}(.*)?$")
