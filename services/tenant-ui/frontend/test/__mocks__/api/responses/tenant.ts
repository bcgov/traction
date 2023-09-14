const self = {
  wallet_id: 'ec8fd0b2-d4c7-4579-a213-14b753ef3b53',
  state: 'active',
  updated_at: '2023-06-26T22:27:20.725045Z',
  connect_to_endorser: [
    {
      endorser_alias: 'endorser',
      ledger_id: 'bcovrin-test',
    },
  ],
  tenant_name: 'Test Tenant',
  tenant_id: '90a3d1fb-c011-4e23-a0b6-fc37d2368467',
  created_at: '2023-06-23T22:24:38.228607Z',
  created_public_did: ['bcovrin-test'],
  enable_ledger_switch: false,
};

const config = {
  connect_to_endorser: [
    {
      endorser_alias: 'endorser',
      ledger_id: 'bcovrin-test',
    },
  ],
  create_public_did: ['bcovrin-test'],
};

const taa = {
  result: {
    aml_record: null,
    taa_record: null,
    taa_required: false,
    taa_accepted: null,
  },
};

const endorserInfo = {
  endorser_did: 'SVfHGCEEvEFmpBPcxgNqRR',
  endorser_name: 'endorser',
};

const endorserConnection = {
  accept: 'manual',
  their_public_did: 'SVfHGCEEvEFmpBPcxgNqRR',
  state: 'active',
  my_did: 'MgnVXbyiF5J44pwj7S9fLr',
  connection_id: '7dcfd983-71f9-4a05-a13b-a2026ed85bb9',
  invitation_mode: 'once',
  routing_state: 'none',
  alias: 'endorser',
  their_did: 'U8NijAj64FGPsBWQReEbdN',
  updated_at: '2023-06-27T18:06:58.559734Z',
  rfc23_state: 'completed',
  created_at: '2023-06-27T18:06:57.441183Z',
  connection_protocol: 'didexchange/1.0',
  their_role: 'inviter',
  request_id: '1f0ae8e3-b956-40c1-8871-3d197b1634f9',
};

const publicDid = {
  result: {
    did: 'BRgEW8XcaTZQkoDXZqWLmP',
    verkey: '6ga1or2Z1fxzmANd7uTick3vKYUoWu3uQwVfWqwo6vCA',
    posture: 'posted',
    key_type: 'ed25519',
    method: 'sov',
  },
};

const connectToEndorser = {
  accept: 'manual',
  their_public_did: 'SVfHGCEEvEFmpBPcxgNqRR',
  state: 'request',
  my_did: 'MgnVXbyiF5J44pwj7S9fLr',
  connection_id: '7dcfd983-71f9-4a05-a13b-a2026ed85bb9',
  invitation_mode: 'once',
  routing_state: 'none',
  alias: 'endorser',
  their_did: 'SVfHGCEEvEFmpBPcxgNqRR',
  updated_at: '2023-06-27T18:06:57.451265Z',
  rfc23_state: 'request-sent',
  created_at: '2023-06-27T18:06:57.441183Z',
  connection_protocol: 'didexchange/1.0',
  their_role: 'inviter',
  request_id: '1f0ae8e3-b956-40c1-8871-3d197b1634f9',
};

const getTenantSubWallet = {
  wallet_id: 'ec8fd0b2-d4c7-4579-a213-14b753ef3b53',
  settings: {
    'wallet.type': 'askar',
    'wallet.name': 'Jamie',
    'wallet.webhook_urls': [],
    'wallet.dispatch_type': 'base',
    default_label: 'Jamie',
    'wallet.id': 'ec8fd0b2-d4c7-4579-a213-14b753ef3b53',
  },
  updated_at: '2023-06-27T17:58:09.989555Z',
  key_management_mode: 'managed',
  created_at: '2023-06-23T22:24:37.068458Z',
};

const updateWallet = {
  created_at: '2021-12-31T23:59:59Z',
  key_management_mode: 'managed',
  settings: {},
  state: 'active',
  updated_at: '2021-12-31T23:59:59Z',
  wallet_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
};

export default {
  config,
  connectToEndorser,
  endorserConnection,
  endorserInfo,
  getTenantSubWallet,
  publicDid,
  self,
  taa,
  updateWallet,
};
