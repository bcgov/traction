import { vi } from 'vitest';

// Some properties have been removed
const credentials = [
  {
    credential_exchange_id: '317850b8-ac52-4dd5-9644-3a898425ecbc',
    auto_offer: false,
    initiator: 'self',
    credential: {
      schema_id: 'KU5ZTAFVKtNKFNpD5Aypzb:2:Test Schema:1.0',
      cred_def_id: 'test-cred_def_id',
    },
    auto_remove: false,
    connection_id: '973a7f8d-7c37-4539-a6a0-83ea8b589103',
    schema_id: 'KU5ZTAFVKtNKFNpD5Aypzb:2:Test Schema:1.0',
    revocation_id: '1',
    auto_issue: true,
    updated_at: '2023-07-13T23:11:38.488544Z',
    state: 'credential_acked',
    credential_definition_id: 'test-cred_def_id',
    role: 'issuer',
    created_at: '2023-07-13T23:06:50.592455Z',
    trace: false,
    credential_offer: {
      schema_id: 'KU5ZTAFVKtNKFNpD5Aypzb:2:Test Schema:1.0',
      cred_def_id: 'test-cred_def_id',
    },
  },
];

const store: { [key: string]: any } = {
  credentials: {
    value: credentials,
  },
  listCredentials: vi.fn().mockResolvedValue(credentials),
  selectedCredential: null,
  offerCredential: vi.fn().mockResolvedValue(true),
  revokeCredential: vi.fn().mockResolvedValue(true),
  deleteCredentialExchange: vi.fn().mockResolvedValue(true),
  getCredentials: vi.fn().mockResolvedValue({}),
};

export { store };
