import { vi } from 'vitest';

// Some properties have been removed
const credentials = [
  {
    cred_ex_record: {
      connection_id: '973a7f8d-7c37-4539-a6a0-83ea8b589103',
      state: 'done',
      created_at: '2023-07-13T23:06:50.592455Z',
      cred_ex_id: '317850b8-ac52-4dd5-9644-3a898425ecbc',
      credential_definition_id: 'test-cred_def_id',
      auto_offer: false,
      auto_issue: true,
      trace: false,
      cred_offer: {
        schema_id: 'KU5ZTAFVKtNKFNpD5Aypzb:2:Test Schema:1.0',
        cred_def_id: 'test-cred_def_id',
      },
    },
    indy: {
      cred_ex_id: '317850b8-ac52-4dd5-9644-3a898425ecbc',
      created_at: '2023-07-13T23:06:50.592455Z',
      rev_reg_id:
        'WgWxqztrNooG92RXvxSTWv:4:WgWxqztrNooG92RXvxSTWv:3:CL:20:tag:CL_ACCUM:0',
      cred_rev_id: '1',
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
