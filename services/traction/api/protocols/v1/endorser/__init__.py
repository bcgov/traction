from api.protocols.v1.endorser.create_cred_def_processor import CreateCredDefProcessor
from api.protocols.v1.endorser.create_cred_def_revocation_processor import (
    CreateCredDefRevocationProcessor,
)
from api.protocols.v1.endorser.create_schema_processor import CreateSchemaProcessor


def subscribe_endorser_protocol_listeners():
    CreateSchemaProcessor()
    CreateCredDefProcessor()
    CreateCredDefRevocationProcessor()
