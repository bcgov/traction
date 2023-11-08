const makeReservationAutoApprove = {
  reservation_id: 'reservation_id',
  reservation_pwd: 'reservation_pwd',
};

const makeReservationVerify = {
  reservation_id: 'reservation_id',
  reservation_pwd: '',
};

const checkIn = {
  wallet_id: 'wallet_id',
  wallet_key: 'wallet_key',
  token: 'token',
};

const reservation = {
  connect_to_endorser: {
    endorser_alias: ' ... ',
    ledger_id: ' ... ',
  },
  contact_email: 'string',
  create_public_did: ['string'],
  created_at: '2021-12-31T23:59:59Z',
  reservation_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
  state: 'requested',
  state_notes: 'string',
  tenant_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
  tenant_name: 'line of business short name',
  updated_at: '2021-12-31T23:59:59Z',
  wallet_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
};

export default {
  checkIn,
  makeReservationAutoApprove,
  makeReservationVerify,
  reservation,
};
