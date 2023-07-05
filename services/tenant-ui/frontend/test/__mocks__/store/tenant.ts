import { vi } from 'vitest';

const store: { [key: string]: any } = {
  tenant: {
    loading: false,
    loadingIssuance: false,
    error: null,
    endorserConnection: null,
    endorserInfo: null,
    publicDid: null,
    publicDidRegistrationProgress: '',
    taa: null,
    tenantConfig: null,
    tenantWallet: null,
    value: {
      tenant_name: 'test',
    },
  },
};

store.getEndorserInfo = vi.fn().mockResolvedValue({
  endorser_did: 'SVfHGCEEvEFmpBPcxgNqRR',
  endorser_name: 'endorser',
});

export { store };
