export const TABLE_OPT = {
  ROWS_DEFAULT: 10,
  ROWS_OPTIONS: [10, 25, 50],
};

export const MESSAGES = {
  TIME_LONG: 86400000, // One day
  TIME_SHORT: 600000, // Ten minutes
};

export const API_PATH = {
  // The tenant UI backend
  CONFIG: '/config',
  EMAIL_CONFIRMATION: '/email/reservationConfirmation',
  EMAIL_STATUS: '/email/reservationStatus',

  // TODO: Align these urls
  OIDC_INNKEEPER_LOGIN: '/api/innkeeperLogin',
  OIDC_INNKEEPER_RESERVATION: '/innkeeperReservation',

  // Acapy and Plugins
  BASICMESSAGES: '/basicmessages',
  BASICMESSAGES_SEND: (connId: string) => `/connections/${connId}/send-message`,

  CONNECTIONS: '/connections',
  CONNECTION: (id: string) => `/connections/${id}`,
  CONNECTIONS_CREATE_INVITATION: '/connections/create-invitation',
  CONNECTIONS_RECEIVE_INVITATION: '/connections/receive-invitation',
  CONNECTIONS_INVITATION: (id: string) => `/connections/${id}/invitation`,
  CONNECTIONS_ENDPOINTS: (id: string) => `/connections/${id}/endpoints`,
  CONNECTIONS_METADATA: (id: string) => `/connections/${id}/metadata`,

  CREDENTIAL_MIME_TYPES: (id: string) => `/credential/mime-types/${id}`,
  CREDENTIAL_REVOKED: (id: string) => `/credential/revoked/${id}`,
  CREDENTIAL_W3C: (id: string) => `/credential/w3c/${id}`,
  CREDENTIAL: (id: string) => `/credential/${id}`,
  CREDENTIALS: '/credentials',
  CREDENTIALS_W3C: '/credentials/w3c',

  CREDENTIAL_DEFINITIONS: '/credential-definitions',
  CREDENTIAL_DEFINITION: (id: string) => `/credential-definitions/${id}`,
  CREDENTIAL_DEFINITIONS_CREATED: '/credential-definitions/created',

  CREDENTIAL_DEFINITION_STORAGE: '/credential-definition-storage',
  CREDENTIAL_DEFINITION_STORAGE_ITEM: (id: string) =>
    `/credential-definition-storage/${id}`,

  DID_EXCHANGE_CREATE_REQUEST: '/didexchange/create-request',
  DID_EXCHANGE_RECIEVE_REQUEST: '/didexchange/recieve-request',
  DID_EXCHANGE_ACCEPT_INVITATION: (id: string) =>
    `/didexchange/${id}/accept-invitation`,
  DID_EXCHANGE_ACCEPT_REQUEST: (id: string) =>
    `/didexchange/${id}/accept-request`,

  INNKEEPER_AUTHENTICATIONS_API: '/innkeeper/authentications/api/',
  INNKEEPER_AUTHENTICATIONS_API_RECORD: (id: string) =>
    `/innkeeper/authentications/api/${id}`,
  INNKEEPER_AUTHENTICATIONS_API_POST: '/innkeeper/authentications/api',
  INNKEEPER_TOKEN: '/innkeeper/token',
  INNKEEPER_TENANTS: '/innkeeper/tenants/',
  INNKEEPER_TENANT: (id: string) => `/innkeeper/tenants/${id}`,
  INNKEEPER_TENANT_CONFIG: (id: string) => `/innkeeper/tenants/${id}/config`,
  INNKEEPER_TENANT_DEFAULT_CONFIG: '/innkeeper/default-config',
  INNKEEPER_RESERVATIONS: '/innkeeper/reservations/',
  INNKEEPER_RESERVATIONS_APPROVE: (id: string) =>
    `/innkeeper/reservations/${id}/approve`,
  INNKEEPER_RESERVATIONS_CONFIG: (id: string) =>
    `/innkeeper/reservations/${id}/config`,
  INNKEEPER_RESERVATIONS_DENY: (id: string) =>
    `/innkeeper/reservations/${id}/deny`,

  ISSUE_CREDENTIAL_RECORDS: '/issue-credential/records',
  ISSUE_CREDENTIAL_RECORD: (id: string) => `/issue-credential/records/${id}`,
  ISSUE_CREDENTIAL_RECORDS_SEND_OFFER: (id: string) =>
    `/issue-credential/records/${id}/send-offer`,
  ISSUE_CREDENTIALS_SEND_OFFER: '/issue-credential/send-offer',
  ISSUE_CREDENTIAL_RECORDS_SEND_REQUEST: (id: string) =>
    `/issue-credential/records/${id}/send-request`,

  LEDGER_TAA: '/ledger/taa',
  LEDGER_TAA_ACCEPT: '/ledger/taa/accept',

  MULTITENANCY_RESERVATIONS: '/multitenancy/reservations',
  MULTITENANCY_RESERVATION: (resId: string) =>
    `/multitenancy/reservations/${resId}`,
  MULTITENANCY_RESERVATION_CHECK_IN: (resId: string) =>
    `/multitenancy/reservations/${resId}/check-in`,
  MULTITENANCY_TENANT_TOKEN: (tenantId: string) =>
    `/multitenancy/tenant/${tenantId}/token`,
  MULTITENANCY_WALLET_TOKEN: (tenantId: string) =>
    `/multitenancy/wallet/${tenantId}/token`,

  OCAS: '/oca',
  OCA: (id: string) => `/oca/${id}`,

  PRESENT_PROOF_CREATE_REQUEST: '/present-proof/create-request',
  PRESENT_PROOF_RECORDS: '/present-proof/records',
  PRESENT_PROOF_RECORD: (id: string) => `/present-proof/records/${id}`,
  PRESENT_PROOF_RECORD_CREDENTIALS: (id: string) =>
    `/present-proof/records/${id}/credentials`,
  PRESENT_PROOF_RECORD_PROBLEM: (id: string) =>
    `/present-proof/records/${id}/problem-report`,
  PRESENT_PROOF_RECORD_SEND_PRESENTATION: (id: string) =>
    `/present-proof/records/${id}/send-presentation`,
  PRESENT_PROOF_RECORD_SEND_REQUEST: (id: string) =>
    `/present-proof/records/${id}/send-request`,
  PRESENT_PROOF_RECORD_VERIFY: (id: string) =>
    `/present-proof/records/${id}/verify-presentation`,
  PRESENT_PROOF_SEND_PROPOSAL: '/present-proof/send-proposal',
  PRESENT_PROOF_SEND_REQUEST: '/present-proof/send-request',

  REVOCATION_REVOKE: '/revocation/revoke',

  SCHEMAS: '/schemas',
  SCHEMA: (id: string) => `/schemas/${id}`,
  SCHEMAS_CREATED: '/schemas/created',
  SCHEMAS_WRITE_RECORD: (id: string) => `/schemas/${id}/write_record`,

  SCHEMA_STORAGE: '/schema-storage',
  SCHEMA_STORAGE_SYNC: '/schema-storage/sync-created',
  SCHEMA_STORAGE_ITEM: (id: string) => `/schema-storage/${id}`,

  TENANT_SELF: '/tenant',
  TENANT_ENDORSER_CONNECTION: '/tenant/endorser-connection',
  TENANT_ENDORSER_INFO: '/tenant/endorser-info',
  TENANT_REGISTER_PUBLIC_DID: '/ledger/register-nym',
  TENANT_GET_VERKEY_POSTED_DID: '/ledger/did-verkey',
  TENANT_SWITCH_WRITE_LEDGER: (id: string) => `/ledger/${id}/set-write-ledger`,
  TENANT_GET_WRITE_LEDGER: '/ledger/get-write-ledger',
  TENANT_CONFIG_SET_LEDGER_ID: '/tenant/config/set-ledger-id',
  TENANT_TOKEN: '/tenant/token',
  TENANT_WALLET: '/tenant/wallet',
  TENANT_CONFIG: '/tenant/config',

  TENANT_AUTHENTICATIONS_API: '/tenant/authentications/api/',
  TENANT_AUTHENTICATIONS_API_RECORD: (id: string) =>
    `/tenant/authentications/api/${id}`,
  TENANT_AUTHENTICATIONS_API_POST: '/tenant/authentications/api',

  TENANT_SETTINGS: '/settings',

  WALLET_DID_PUBLIC: '/wallet/did/public',
  WALLET_DID_CREATE: '/wallet/did/create',

  SERVER_PLUGINS: '/plugins',
  TRANSACTION_GET: (id: string) => `/transactions/${id}`,

  // Legacy (to be removed)

  HOLDER_CREDENTIALS: '/tenant/v1/holder/credentials/',
  HOLDER_CREDENTIALS_ACCEPT_OFFER: (id: string) =>
    `/tenant/v1/holder/credentials/${id}/accept-offer`,
  HOLDER_CREDENTIALS_REJECT_OFFER: (id: string) =>
    `/tenant/v1/holder/credentials/${id}/reject-offer`,
  HOLDER_CREDENTIAL: (id: string) => `/tenant/v1/holder/credentials/${id}`,
  HOLDER_PRESENTATIONS: '/tenant/v1/holder/presentations/',
  HOLDER_PRESENTATION: (id: string) => `/tenant/v1/holder/presentations/${id}`,

  ISSUER_CREDENTIAL_REVOKE: (id: string) =>
    `/tenant/v1/issuer/credentials/${id}/revoke-credential`,

  // Testing
  TEST_TENANT_PROXY: '/test',
};

export const CONNECTION_STATUSES = {
  INVITATION: 'invitation',
  ACTIVE: 'active',
  RESPONSE: 'response',
};

export const RESERVATION_STATUSES = {
  APPROVED: 'approved',
  CHECKED_IN: 'checked_in',
  DENIED: 'denied',
  REQUESTED: 'requested',
  // Not an API status, but the state on the FE when just checked-in
  // so they can one-time see the wallet key
  SHOW_WALLET: 'show_wallet',
  // Not API response but show on the FE when it 404s
  NOT_FOUND: 'not_found',
};

export const RESERVATION_STATUS_ROUTE = 'check-status';

// json editor config
export const JSON_EDITOR_DEFAULTS = {
  mainMenuBar: false,
  mode: 'text' as any,
  statusBar: false,
  navigationBar: false,
  indentation: 2,
  tabSize: 2,
};
