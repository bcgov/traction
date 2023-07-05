const listConnections = {
  results: [
    {
      accept: 'auto',
      state: 'active',
      my_did: 'BEQWiPfQXj9q9DYePziaJ2',
      connection_id: 'bb6f8738-b3ee-46e4-b979-a84e6b269a0a',
      invitation_key: 'B6nQE8AjZHoYC3VgDapLGbD8iZJ6cHAepMq3evLaq6hg',
      invitation_mode: 'once',
      routing_state: 'none',
      alias: 'test',
      their_did: 'Tr23L12egq68Ei3Q8uYAeg',
      updated_at: '2023-06-26T22:28:49.084854Z',
      their_label: 'BC Wallet',
      rfc23_state: 'completed',
      created_at: '2023-06-26T22:28:19.163437Z',
      connection_protocol: 'connections/1.0',
      their_role: 'invitee',
    },
    {
      accept: 'auto',
      state: 'active',
      my_did: 'SW9RZUxWXBgSpSvLUgS7Ne',
      connection_id: '97bacd18-2b4e-47e8-81b4-a7e7c7ef64d7',
      invitation_key: 'BHYQq7uYgvtEECn2zXSbig5NVqU7vaeDF2auLVPNDdhF',
      invitation_mode: 'once',
      routing_state: 'none',
      their_did: 'QXpNavd16ts8MocfWTFMT8',
      updated_at: '2023-06-26T22:30:51.933421Z',
      their_label: 'BC Wallet',
      rfc23_state: 'completed',
      created_at: '2023-06-26T22:30:51.421112Z',
      connection_protocol: 'connections/1.0',
      their_role: 'invitee',
    },
  ],
};

const createConnectionResponse = {
  connection_id: 'ca1f226e-626c-43dd-b063-dcd06861d116',
  invitation: {
    '@type': 'https://didcomm.org/connections/1.0/invitation',
    '@id': 'fb084711-ab6f-4588-b644-bacfd7a2aedc',
    label: 'Jamie',
    recipientKeys: ['6dS92vrNX8eWmxUGVc4ffi7goYZ6JzPCrpwcsWTwi9zu'],
    serviceEndpoint: 'https://2682-70-66-140-105.ngrok-free.app',
  },
  invitation_url:
    'https://2682-70-66-140-105.ngrok-free.app?c_i=eyJAdHlwZSI6ICJodHRwczovL2RpZGNvbW0ub3JnL2Nvbm5lY3Rpb25zLzEuMC9pbnZpdGF0aW9uIiwgIkBpZCI6ICJmYjA4NDcxMS1hYjZmLTQ1ODgtYjY0NC1iYWNmZDdhMmFlZGMiLCAibGFiZWwiOiAiSmFtaWUiLCAicmVjaXBpZW50S2V5cyI6IFsiNmRTOTJ2ck5YOGVXbXhVR1ZjNGZmaTdnb1laNkp6UENycHdjc1dUd2k5enUiXSwgInNlcnZpY2VFbmRwb2ludCI6ICJodHRwczovLzI2ODItNzAtNjYtMTQwLTEwNS5uZ3Jvay1mcmVlLmFwcCJ9',
  alias: 'test.invitation',
};

const receiveInvitationResponse = {
  accept: 'auto',
  state: 'request',
  my_did: 'CV6hpNHfEZC6XiUdNeHSpX',
  connection_id: '0dbf3d6d-ae96-4c81-8e6a-24350fd830ff',
  invitation_key: '7pZ4SMd7KBDSqPT2HUnsbocJ1YjZQMrzzcGcsfN5NfTr',
  invitation_mode: 'once',
  routing_state: 'none',
  invitation_msg_id: '8fbc2934-f7d1-4f46-aa98-41252847b3b9',
  alias: 'faber.agent',
  updated_at: '2023-06-30T22:04:05.287225Z',
  their_label: 'Jamie',
  rfc23_state: 'request-sent',
  created_at: '2023-06-30T22:04:05.229798Z',
  connection_protocol: 'connections/1.0',
  their_role: 'inviter',
  request_id: '657093be-86dd-4650-86b9-ea8ed454997d',
};

export default {
  createConnectionResponse,
  listConnections,
  receiveInvitationResponse,
};
