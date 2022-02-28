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
