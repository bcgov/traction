import { vi } from 'vitest';

const tenant = {
  created_public_did: ['bcovrin-test'],
  wallet_id: 'ec8fd0b2-d4c7-4579-a213-14b753ef3b53',
  connect_to_endorser: [
    {
      endorser_alias: 'endorser',
      ledger_id: 'bcovrin-test',
    },
  ],
  tenant_name: 'Tenant',
  created_at: '2023-06-23T22:24:38.228607Z',
  tenant_id: '90a3d1fb-c011-4e23-a0b6-fc37d2368467',
  state: 'active',
  enable_ledger_switch: true,
};

const store: { [key: string]: any } = {
  tenants: {
    value: [tenant],
  },
  serverConfig: {
    value: {
      config: {
        version: '1.1.0',
      },
    },
  },
  listTenants: vi.fn().mockResolvedValue([tenant]).mockRejectedValue('fail'),
  getServerConfig: vi.fn().mockResolvedValue('success'),
};

export { store };
