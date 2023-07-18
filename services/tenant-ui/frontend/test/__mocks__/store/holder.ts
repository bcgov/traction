import { vi } from 'vitest';

// Some properties have been removed
const credentials = [
  {
    credential_exchange_id: '60dbbdab-50ea-4684-873c-d56f965dea10',
    auto_offer: false,
    initiator: 'external',
    credential: {
      referent: 'da48ff15-be1d-4745-b46d-6ef7f4e5dff5',
      attrs: {
        age: '',
      },
      schema_id: 'test-schema_id',
      cred_def_id: 'test-cred_def_id',
      rev_reg_id:
        'KU5ZTAFVKtNKFNpD5Aypzb:4:test-cred_def_id:CL_ACCUM:ea59e414-2803-40bd-8941-87fb1a47e55f',
      cred_rev_id: '1',
    },
    auto_remove: false,
    connection_id: '76e1b8bf-8650-4315-b726-b669867c5fb2',
    schema_id: 'test-schema_id',
    revocation_id: '1',
    role: 'holder',
    created_at: '2023-07-13T23:06:51.062050Z',
    trace: false,
  },
];

// Some properties have been removed
const credentialExchanges = [
  {
    credential_exchange_id: '60dbbdab-50ea-4684-873c-d56f965dea10',
    auto_offer: false,
    initiator: 'external',
    credential: {
      referent: 'da48ff15-be1d-4745-b46d-6ef7f4e5dff5',
      attrs: {
        age: '',
      },
      schema_id: 'test-schema_id',
      cred_def_id: 'test-cred_def_id',
      rev_reg_id:
        'KU5ZTAFVKtNKFNpD5Aypzb:4:test-cred_def_id:CL_ACCUM:ea59e414-2803-40bd-8941-87fb1a47e55f',
      cred_rev_id: '1',
    },
    auto_remove: false,
    connection_id: '76e1b8bf-8650-4315-b726-b669867c5fb2',
    schema_id: 'test-schema_id',
    revocation_id: '1',
    auto_issue: false,
    updated_at: '2023-07-13T23:11:38.367573Z',
    credential_id: 'da48ff15-be1d-4745-b46d-6ef7f4e5dff5',
    state: 'credential_acked',
    credential_definition_id: 'test-cred_def_id',
    role: 'holder',
    created_at: '2023-07-13T23:06:51.062050Z',
    trace: false,
  },
];

const store: { [key: string]: any } = {
  credentials: {
    value: credentials,
  },
  credentialExchanges: {
    value: credentialExchanges,
  },
  listCredentials: vi.fn().mockResolvedValue(credentials),
  selectedCredential: null,
  listHolderCredentialExchanges: vi.fn().mockResolvedValue(true),
};

export { store };
