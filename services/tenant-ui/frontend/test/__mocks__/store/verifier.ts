import { vi } from 'vitest';

const presentations = [
  {
    auto_verify: false,
    thread_id: 'cae3c85c-27c6-478f-bcec-347e6c8fe7f8',
    role: 'prover',
    created_at: '2023-07-13T21:32:33.659216Z',
    trace: false,
    connection_id: '973a7f8d-7c37-4539-a6a0-83ea8b589103',
    presentation_exchange_id: 'aa0de458-c9b4-4e8e-949e-6216a1bab59f',
    presentation_request: {
      nonce: '1234567890',
      name: 'proof-request',
      version: '1.0',
      requested_attributes: {
        studentInfo: {
          restrictions: [
            {
              schema_name: 'student id',
            },
          ],
          names: ['given_names', 'family_name'],
        },
      },
      requested_predicates: {
        not_expired: {
          p_value: 20230527,
          restrictions: [
            {
              schema_name: 'student id',
            },
          ],
          p_type: '>=',
          name: 'expiry_dateint',
        },
      },
    },
    presentation_request_dict: {
      '@type': 'https://didcomm.org/present-proof/1.0/request-presentation',
      '@id': 'cae3c85c-27c6-478f-bcec-347e6c8fe7f8',
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
    initiator: 'external',
    updated_at: '2023-07-13T21:32:33.659216Z',
    state: 'request_received',
  },
];

const store: { [key: string]: any } = {
  // Not sure why this can't use object with value property like other mocks
  presentations,
  listPresentations: vi.fn().mockResolvedValue(presentations),
  selectedPresentation: null,
  getPresentation: vi.fn().mockResolvedValue({}),
  deleteRecord: vi.fn().mockResolvedValue(true),
  sendPresentaitonRequest: vi.fn().mockResolvedValue(true),
  loading: false,
};

export { store };
