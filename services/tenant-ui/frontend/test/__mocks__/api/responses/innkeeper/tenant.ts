const reservations = {
  results: [
    {
      connect_to_endorsers: {
        endorser_alias: ' ... ',
        ledger_id: ' ... ',
      },
      contact_email: 'string',
      contact_name: 'string',
      contact_phone: 'string',
      create_public_did: ['string'],
      created_at: '2021-12-31T23:59:59Z',
      reservation_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
      state: 'requested',
      state_notes: 'string',
      tenant_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
      tenant_name: 'line of business short name',
      tenant_reason: 'Issue permits to clients',
      updated_at: '2021-12-31T23:59:59Z',
      wallet_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    },
  ],
};

const approveReservation = {
  reservation_pwd: 'string',
};

const denyReservation = {
  reservation_id: 'string',
};

const tenants = {
  results: [
    {
      connected_to_endorsers: {
        endorser_alias: ' ... ',
        ledger_id: ' ... ',
      },
      created_at: '2021-12-31T23:59:59Z',
      created_public_did: ['string'],
      state: 'active',
      tenant_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
      tenant_name: 'line of business short name',
      updated_at: '2021-12-31T23:59:59Z',
      wallet_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    },
  ],
};

const updateTenant = {
  connected_to_endorsers: {
    endorser_alias: ' ... ',
    ledger_id: ' ... ',
  },
  created_at: '2021-12-31T23:59:59Z',
  created_public_did: ['string'],
  state: 'active',
  tenant_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
  tenant_name: 'line of business short name',
  updated_at: '2021-12-31T23:59:59Z',
  wallet_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
};

export default {
  approveReservation,
  denyReservation,
  updateTenant,
  reservations,
  tenants,
};
