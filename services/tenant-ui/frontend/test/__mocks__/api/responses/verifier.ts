const presentProofRecords = {
  results: [
    {
      presentation_request: {
        nonce: '1234567890',
        name: 'proof-request',
        version: '1.0',
        requested_attributes: {
          studentInfo: {
            names: ['given_names', 'family_name'],
            restrictions: [
              {
                schema_name: 'student id',
              },
            ],
          },
        },
        requested_predicates: {
          not_expired: {
            restrictions: [
              {
                schema_name: 'student id',
              },
            ],
            p_value: 20230527,
            name: 'expiry_dateint',
            p_type: '>=',
          },
        },
      },
      presentation_exchange_id: 'c95d7f65-13dc-4145-a314-e01ed6a0fddf',
      thread_id: 'a59428ae-d349-48fa-8cc0-61d1bb111d19',
      auto_verify: false,
      state: 'request_sent',
      connection_id: '97bacd18-2b4e-47e8-81b4-a7e7c7ef64d7',
      initiator: 'self',
      auto_present: false,
      trace: false,
      updated_at: '2023-06-27T21:14:54.152520Z',
      presentation_request_dict: {
        '@type': 'https://didcomm.org/present-proof/1.0/request-presentation',
        '@id': 'a59428ae-d349-48fa-8cc0-61d1bb111d19',
        'request_presentations~attach': [
          {
            '@id': 'libindy-request-presentation-0',
            'mime-type': 'application/json',
            data: {
              base64:
                'eyJuYW1lIjogInByb29mLXJlcXVlc3QiLCAibm9uY2UiOiAiMTIzNDU2Nzg5MCIsICJ2ZXJzaW9uIjogIjEuMCIsICJyZXF1ZXN0ZWRfYXR0cmlidXRlcyI6IHsic3R1ZGVudEluZm8iOiB7Im5hbWVzIjogWyJnaXZlbl9uYW1lcyIsICJmYW1pbHlfbmFtZSJdLCAicmVzdHJpY3Rpb25zIjogW3sic2NoZW1hX25hbWUiOiAic3R1ZGVudCBpZCJ9XX19LCAicmVxdWVzdGVkX3ByZWRpY2F0ZXMiOiB7Im5vdF9leHBpcmVkIjogeyJuYW1lIjogImV4cGlyeV9kYXRlaW50IiwgInBfdHlwZSI6ICI+PSIsICJwX3ZhbHVlIjogMjAyMzA1MjcsICJyZXN0cmljdGlvbnMiOiBbeyJzY2hlbWFfbmFtZSI6ICJzdHVkZW50IGlkIn1dfX19',
            },
          },
        ],
        comment: '',
      },
      role: 'verifier',
      created_at: '2023-06-27T21:14:54.152520Z',
    },
  ],
};

const presentProofRecord = {
  presentation_request: {
    nonce: '1234567890',
    name: 'proof-request',
    version: '1.0',
    requested_attributes: {
      studentInfo: {
        names: ['given_names', 'family_name'],
        restrictions: [
          {
            schema_name: 'student id',
          },
        ],
      },
    },
    requested_predicates: {
      not_expired: {
        restrictions: [
          {
            schema_name: 'student id',
          },
        ],
        p_value: 20230527,
        name: 'expiry_dateint',
        p_type: '>=',
      },
    },
  },
  presentation_exchange_id: 'c95d7f65-13dc-4145-a314-e01ed6a0fddf',
  thread_id: 'a59428ae-d349-48fa-8cc0-61d1bb111d19',
  auto_verify: false,
  state: 'request_sent',
  connection_id: '97bacd18-2b4e-47e8-81b4-a7e7c7ef64d7',
  initiator: 'self',
  auto_present: false,
  trace: false,
  updated_at: '2023-06-27T21:14:54.152520Z',
  presentation_request_dict: {
    '@type': 'https://didcomm.org/present-proof/1.0/request-presentation',
    '@id': 'a59428ae-d349-48fa-8cc0-61d1bb111d19',
    'request_presentations~attach': [
      {
        '@id': 'libindy-request-presentation-0',
        'mime-type': 'application/json',
        data: {
          base64:
            'eyJuYW1lIjogInByb29mLXJlcXVlc3QiLCAibm9uY2UiOiAiMTIzNDU2Nzg5MCIsICJ2ZXJzaW9uIjogIjEuMCIsICJyZXF1ZXN0ZWRfYXR0cmlidXRlcyI6IHsic3R1ZGVudEluZm8iOiB7Im5hbWVzIjogWyJnaXZlbl9uYW1lcyIsICJmYW1pbHlfbmFtZSJdLCAicmVzdHJpY3Rpb25zIjogW3sic2NoZW1hX25hbWUiOiAic3R1ZGVudCBpZCJ9XX19LCAicmVxdWVzdGVkX3ByZWRpY2F0ZXMiOiB7Im5vdF9leHBpcmVkIjogeyJuYW1lIjogImV4cGlyeV9kYXRlaW50IiwgInBfdHlwZSI6ICI+PSIsICJwX3ZhbHVlIjogMjAyMzA1MjcsICJyZXN0cmljdGlvbnMiOiBbeyJzY2hlbWFfbmFtZSI6ICJzdHVkZW50IGlkIn1dfX19',
        },
      },
    ],
    comment: '',
  },
  role: 'verifier',
  created_at: '2023-06-27T21:14:54.152520Z',
};

export default {
  presentProofRecords,
  presentProofRecord,
};
