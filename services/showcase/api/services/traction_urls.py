from api.core.config import settings

# ROOT
R = settings.TRACTION_ENDPOINT

# SUB APP ROOTS
R_INN = f"{R}/innkeeper"
R_INN_V1 = f"{R_INN}/v1"

R_TNT = f"{R}/tenant"
R_TNT_V1 = f"{R_TNT}/v1"

# INNKEEPER
INNKEEPER_TOKEN = f"{R_INN}/token"
INNKEEPER_CHECKIN = f"{R_INN_V1}/check-in"
INNKEEPER_MAKE_ISSUER = f"{R_INN_V1}/issuers"


# TENANT
TENANT_TOKEN = f"{R_TNT}/token"
TENANT_GET_CONNECTIONS = f"{R_TNT_V1}/connections"
TENANT_CREATE_INVITATION = f"{R_TNT_V1}/connections/create-invitation"
TENANT_RECEIVE_INVITATION = f"{R_TNT_V1}/connections/receive-invitation"
TENANT_ADMIN_WEBHOOK = f"{R_TNT_V1}/admin/webhook"
TENANT_MAKE_ISSUER = f"{R_TNT_V1}/admin/issuer"
TENANT_CREATE_SCHEMA = f"{R_TNT_V1}/admin/schema"
TENANT_CREDENTIAL_ISSUE = f"{R_TNT_V1}/credentials/issuer/issue"
TENANT_CREDENTIAL_REVOKE = f"{R_TNT_V1}/credentials/issuer/revoke"
TENANT_GET_CRED_OFFERS = f"{R_TNT_V1}/credentials/holder/offer"
TENANT_ACCEPT_CRED_OFFER = f"{R_TNT_V1}/credentials/holder/accept_offer"
TENANT_REJECT_CRED_OFFER = f"{R_TNT_V1}/credentials/holder/reject_offer"
TENANT_GET_CREDENTIALS = f"{R_TNT_V1}/credentials/holder/"
TENANT_VERIFIER_REQUEST_CREDENTIALS = f"{R_TNT_V1}/credentials/verifier/request"
TENANT_HOLDER_CREDENTIALS_FOR_REQ = f"{R_TNT_V1}/credentials/holder/creds-for-request"
TENANT_HOLDER_CREDENTIAL_REQUESTS = f"{R_TNT_V1}/credentials/holder/request"
TENANT_HOLDER_PRESENT_CREDS = f"{R_TNT_V1}/credentials/holder/present-credential"
TENANT_HOLDER_CREDENTIAL_REQUEST_REJECT = (
    f"{R_TNT_V1}/credentials/holder/reject-request"
)
