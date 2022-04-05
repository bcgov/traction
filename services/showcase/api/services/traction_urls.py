from api.core.config import settings

# ROOT
R = settings.TRACTION_ENDPOINT

# SUB APP ROOTS
R_INN = f"{R}/innkeeper"
R_INN_V0 = f"{R_INN}/v0"
R_INN_V1 = f"{R_INN}/v1"
R_INN_VER = R_INN_V0

R_TNT = f"{R}/tenant"
R_TNT_V0 = f"{R_TNT}/v0"
R_TNT_V1 = f"{R_TNT}/v1"
R_TNT_VER = R_TNT_V0

# INNKEEPER
INNKEEPER_TOKEN = f"{R_INN}/token"
INNKEEPER_CHECKIN = f"{R_INN_VER}/check-in"
INNKEEPER_MAKE_ISSUER = f"{R_INN_VER}/issuers"


# TENANT
TENANT_TOKEN = f"{R_TNT}/token"
TENANT_GET_CONNECTIONS = f"{R_TNT_VER}/connections"
TENANT_CREATE_INVITATION = f"{R_TNT_VER}/connections/create-invitation"
TENANT_RECEIVE_INVITATION = f"{R_TNT_VER}/connections/receive-invitation"
TENANT_ADMIN_WEBHOOK = f"{R_TNT_VER}/admin/webhook"
TENANT_MAKE_ISSUER = f"{R_TNT_VER}/admin/issuer"
TENANT_CREATE_SCHEMA = f"{R_TNT_VER}/admin/schema"
TENANT_CREDENTIAL_ISSUE = f"{R_TNT_VER}/credentials/issuer/issue"
TENANT_CREDENTIAL_REVOKE = f"{R_TNT_VER}/credentials/issuer/revoke"
TENANT_GET_CRED_OFFERS = f"{R_TNT_VER}/credentials/holder/offer"
TENANT_ACCEPT_CRED_OFFER = f"{R_TNT_VER}/credentials/holder/accept_offer"
TENANT_REJECT_CRED_OFFER = f"{R_TNT_VER}/credentials/holder/reject_offer"
TENANT_GET_CREDENTIALS = f"{R_TNT_VER}/credentials/holder/"
TENANT_VERIFIER_REQUEST_CREDENTIALS = f"{R_TNT_VER}/credentials/verifier/request"
TENANT_HOLDER_CREDENTIALS_FOR_REQ = f"{R_TNT_VER}/credentials/holder/creds-for-request"
TENANT_HOLDER_CREDENTIAL_REQUESTS = f"{R_TNT_VER}/credentials/holder/request"
TENANT_HOLDER_PRESENT_CREDS = f"{R_TNT_VER}/credentials/holder/present-credential"
TENANT_HOLDER_CREDENTIAL_REQUEST_REJECT = (
    f"{R_TNT_VER}/credentials/holder/reject-request"
)
