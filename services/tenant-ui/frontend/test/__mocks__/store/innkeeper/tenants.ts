import { vi } from 'vitest';

const tenant = {
  created_public_did: ['bcovrin-test'],
  wallet_id: 'ec8fd0b2-d4c7-4579-a213-14b753ef3b53',
  connected_to_endorsers: [
    {
      endorser_alias: 'endorser',
      ledger_id: 'bcovrin-test',
    },
  ],
  tenant_name: 'Tenant',
  created_at: '2023-06-23T22:24:38.228607Z',
  tenant_id: '90a3d1fb-c011-4e23-a0b6-fc37d2368467',
  state: 'active',
};

const store: { [key: string]: any } = {
  tenants: {
    value: [tenant],
  },
  listTenants: vi.fn().mockResolvedValue([tenant]).mockRejectedValue('fail'),
};

export { store };
