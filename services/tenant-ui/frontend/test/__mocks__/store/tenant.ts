import { vi } from 'vitest';

const store: { [key: string]: any } = {
  clearTenant: vi.fn(),
  tenant: {
    value: {
      tenant_name: 'test',
    },
  },
  endorserInfo: {
    value: null,
  },
  serverConfig: {
    value: {
      config: {
        version: '1.1.0',
      },
    },
  },
  getEndorserInfo: vi.fn().mockResolvedValue({
    endorser_did: 'SVfHGCEEvEFmpBPcxgNqRR',
    endorser_name: 'endorser',
  }),
  getIssuanceStatus: vi.fn().mockResolvedValue('success'),
  getSelf: vi.fn().mockResolvedValue('success'),
  getTenantConfig: vi.fn().mockResolvedValue('success'),
  getServerConfig: vi.fn().mockResolvedValue('success'),
};

export { store };
