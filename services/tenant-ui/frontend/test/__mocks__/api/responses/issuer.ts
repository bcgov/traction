const credentials = {
  results: [
    {
      auto_issue: false,
      auto_offer: false,
      auto_remove: false,
      connection_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
      created_at: '2021-12-31T23:59:59Z',
      credential: {
        attrs: {
          additionalProp1: 'alice',
          additionalProp2: 'alice',
          additionalProp3: 'alice',
        },
        cred_def_id: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
        cred_rev_id: '12345',
        referent: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
        rev_reg_id:
          'WgWxqztrNooG92RXvxSTWv:4:WgWxqztrNooG92RXvxSTWv:3:CL:20:tag:CL_ACCUM:0',
        schema_id: 'WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0',
      },
      credential_definition_id: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
      credential_exchange_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
      credential_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
      credential_offer: {
        cred_def_id: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
        key_correctness_proof: {
          c: '0',
          xr_cap: [['string']],
          xz_cap: '0',
        },
        nonce: '0',
        schema_id: 'WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0',
      },
      credential_offer_dict: {
        '@id': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
        '@type': 'https://didcomm.org/my-family/1.0/my-message-type',
        comment: 'string',
        credential_preview: {
          '@type': 'issue-credential/1.0/credential-preview',
          attributes: [
            {
              'mime-type': 'image/jpeg',
              name: 'favourite_drink',
              value: 'martini',
            },
          ],
        },
        'offers~attach': [
          {
            '@id': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
            byte_count: 1234,
            data: {
              base64: 'ey4uLn0=',
              json: {
                sample: 'content',
              },
              jws: {
                header: {
                  kid: 'did:sov:LjgpST2rjsoxYegQDRm7EL#keys-4',
                },
                protected: 'ey4uLn0',
                signature: 'ey4uLn0',
                signatures: [
                  {
                    header: {
                      kid: 'did:sov:LjgpST2rjsoxYegQDRm7EL#keys-4',
                    },
                    protected: 'ey4uLn0',
                    signature: 'ey4uLn0',
                  },
                ],
              },
              links: ['https://link.to/data'],
              sha256:
                '617a48c7c8afe0521efdc03e5bb0ad9e655893e6b4b51f0e794d70fba132aacb',
            },
            description: 'view from doorway, facing east, with lights off',
            filename: 'IMG1092348.png',
            lastmod_time: '2021-12-31T23:59:59Z',
            'mime-type': 'image/png',
          },
        ],
      },
      credential_proposal_dict: {
        '@id': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
        '@type': 'https://didcomm.org/my-family/1.0/my-message-type',
        comment: 'string',
        cred_def_id: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
        credential_proposal: {
          '@type': 'issue-credential/1.0/credential-preview',
          attributes: [
            {
              'mime-type': 'image/jpeg',
              name: 'favourite_drink',
              value: 'martini',
            },
          ],
        },
        issuer_did: 'WgWxqztrNooG92RXvxSTWv',
        schema_id: 'WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0',
        schema_issuer_did: 'WgWxqztrNooG92RXvxSTWv',
        schema_name: 'string',
        schema_version: '1.0',
      },
      credential_request: {
        blinded_ms: {},
        blinded_ms_correctness_proof: {},
        cred_def_id: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
        nonce: '0',
        prover_did: 'WgWxqztrNooG92RXvxSTWv',
      },
      credential_request_metadata: {},
      error_msg: 'Credential definition identifier is not set in proposal',
      initiator: 'self',
      parent_thread_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
      raw_credential: {
        cred_def_id: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
        rev_reg: {},
        rev_reg_id:
          'WgWxqztrNooG92RXvxSTWv:4:WgWxqztrNooG92RXvxSTWv:3:CL:20:tag:CL_ACCUM:0',
        schema_id: 'WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0',
        signature: {},
        signature_correctness_proof: {},
        values: {
          additionalProp1: {
            encoded: '-1',
            raw: 'string',
          },
          additionalProp2: {
            encoded: '-1',
            raw: 'string',
          },
          additionalProp3: {
            encoded: '-1',
            raw: 'string',
          },
        },
        witness: {},
      },
      revoc_reg_id: 'string',
      revocation_id: 'string',
      role: 'issuer',
      schema_id: 'WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0',
      state: 'credential_acked',
      thread_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
      trace: true,
      updated_at: '2021-12-31T23:59:59Z',
    },
  ],
};

const credential = {
  auto_issue: false,
  auto_offer: false,
  auto_remove: false,
  connection_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
  created_at: '2021-12-31T23:59:59Z',
  credential: {
    attrs: {
      additionalProp1: 'alice',
      additionalProp2: 'alice',
      additionalProp3: 'alice',
    },
    cred_def_id: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
    cred_rev_id: '12345',
    referent: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    rev_reg_id:
      'WgWxqztrNooG92RXvxSTWv:4:WgWxqztrNooG92RXvxSTWv:3:CL:20:tag:CL_ACCUM:0',
    schema_id: 'WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0',
  },
  credential_definition_id: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
  credential_exchange_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
  credential_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
  credential_offer: {
    cred_def_id: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
    key_correctness_proof: {
      c: '0',
      xr_cap: [['string']],
      xz_cap: '0',
    },
    nonce: '0',
    schema_id: 'WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0',
  },
  credential_offer_dict: {
    '@id': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    '@type': 'https://didcomm.org/my-family/1.0/my-message-type',
    comment: 'string',
    credential_preview: {
      '@type': 'issue-credential/1.0/credential-preview',
      attributes: [
        {
          'mime-type': 'image/jpeg',
          name: 'favourite_drink',
          value: 'martini',
        },
      ],
    },
    'offers~attach': [
      {
        '@id': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
        byte_count: 1234,
        data: {
          base64: 'ey4uLn0=',
          json: {
            sample: 'content',
          },
          jws: {
            header: {
              kid: 'did:sov:LjgpST2rjsoxYegQDRm7EL#keys-4',
            },
            protected: 'ey4uLn0',
            signature: 'ey4uLn0',
            signatures: [
              {
                header: {
                  kid: 'did:sov:LjgpST2rjsoxYegQDRm7EL#keys-4',
                },
                protected: 'ey4uLn0',
                signature: 'ey4uLn0',
              },
            ],
          },
          links: ['https://link.to/data'],
          sha256:
            '617a48c7c8afe0521efdc03e5bb0ad9e655893e6b4b51f0e794d70fba132aacb',
        },
        description: 'view from doorway, facing east, with lights off',
        filename: 'IMG1092348.png',
        lastmod_time: '2021-12-31T23:59:59Z',
        'mime-type': 'image/png',
      },
    ],
  },
  credential_proposal_dict: {
    '@id': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    '@type': 'https://didcomm.org/my-family/1.0/my-message-type',
    comment: 'string',
    cred_def_id: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
    credential_proposal: {
      '@type': 'issue-credential/1.0/credential-preview',
      attributes: [
        {
          'mime-type': 'image/jpeg',
          name: 'favourite_drink',
          value: 'martini',
        },
      ],
    },
    issuer_did: 'WgWxqztrNooG92RXvxSTWv',
    schema_id: 'WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0',
    schema_issuer_did: 'WgWxqztrNooG92RXvxSTWv',
    schema_name: 'string',
    schema_version: '1.0',
  },
  credential_request: {
    blinded_ms: {},
    blinded_ms_correctness_proof: {},
    cred_def_id: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
    nonce: '0',
    prover_did: 'WgWxqztrNooG92RXvxSTWv',
  },
  credential_request_metadata: {},
  error_msg: 'Credential definition identifier is not set in proposal',
  initiator: 'self',
  parent_thread_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
  raw_credential: {
    cred_def_id: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
    rev_reg: {},
    rev_reg_id:
      'WgWxqztrNooG92RXvxSTWv:4:WgWxqztrNooG92RXvxSTWv:3:CL:20:tag:CL_ACCUM:0',
    schema_id: 'WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0',
    signature: {},
    signature_correctness_proof: {},
    values: {
      additionalProp1: {
        encoded: '-1',
        raw: 'string',
      },
      additionalProp2: {
        encoded: '-1',
        raw: 'string',
      },
      additionalProp3: {
        encoded: '-1',
        raw: 'string',
      },
    },
    witness: {},
  },
  revoc_reg_id: 'string',
  revocation_id: 'string',
  role: 'issuer',
  schema_id: 'WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0',
  state: 'credential_acked',
  thread_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
  trace: true,
  updated_at: '2021-12-31T23:59:59Z',
};

const sendOffer = {
  auto_issue: false,
  auto_offer: false,
  auto_remove: false,
  connection_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
  created_at: '2021-12-31T23:59:59Z',
  credential: {
    attrs: {
      additionalProp1: 'alice',
      additionalProp2: 'alice',
      additionalProp3: 'alice',
    },
    cred_def_id: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
    cred_rev_id: '12345',
    referent: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    rev_reg_id:
      'WgWxqztrNooG92RXvxSTWv:4:WgWxqztrNooG92RXvxSTWv:3:CL:20:tag:CL_ACCUM:0',
    schema_id: 'WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0',
  },
  credential_definition_id: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
  credential_exchange_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
  credential_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
  credential_offer: {
    cred_def_id: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
    key_correctness_proof: {
      c: '0',
      xr_cap: [['string']],
      xz_cap: '0',
    },
    nonce: '0',
    schema_id: 'WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0',
  },
  credential_offer_dict: {
    '@id': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    '@type': 'https://didcomm.org/my-family/1.0/my-message-type',
    comment: 'string',
    credential_preview: {
      '@type': 'issue-credential/1.0/credential-preview',
      attributes: [
        {
          'mime-type': 'image/jpeg',
          name: 'favourite_drink',
          value: 'martini',
        },
      ],
    },
    'offers~attach': [
      {
        '@id': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
        byte_count: 1234,
        data: {
          base64: 'ey4uLn0=',
          json: {
            sample: 'content',
          },
          jws: {
            header: {
              kid: 'did:sov:LjgpST2rjsoxYegQDRm7EL#keys-4',
            },
            protected: 'ey4uLn0',
            signature: 'ey4uLn0',
            signatures: [
              {
                header: {
                  kid: 'did:sov:LjgpST2rjsoxYegQDRm7EL#keys-4',
                },
                protected: 'ey4uLn0',
                signature: 'ey4uLn0',
              },
            ],
          },
          links: ['https://link.to/data'],
          sha256:
            '617a48c7c8afe0521efdc03e5bb0ad9e655893e6b4b51f0e794d70fba132aacb',
        },
        description: 'view from doorway, facing east, with lights off',
        filename: 'IMG1092348.png',
        lastmod_time: '2021-12-31T23:59:59Z',
        'mime-type': 'image/png',
      },
    ],
  },
  credential_proposal_dict: {
    '@id': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    '@type': 'https://didcomm.org/my-family/1.0/my-message-type',
    comment: 'string',
    cred_def_id: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
    credential_proposal: {
      '@type': 'issue-credential/1.0/credential-preview',
      attributes: [
        {
          'mime-type': 'image/jpeg',
          name: 'favourite_drink',
          value: 'martini',
        },
      ],
    },
    issuer_did: 'WgWxqztrNooG92RXvxSTWv',
    schema_id: 'WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0',
    schema_issuer_did: 'WgWxqztrNooG92RXvxSTWv',
    schema_name: 'string',
    schema_version: '1.0',
  },
  credential_request: {
    blinded_ms: {},
    blinded_ms_correctness_proof: {},
    cred_def_id: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
    nonce: '0',
    prover_did: 'WgWxqztrNooG92RXvxSTWv',
  },
  credential_request_metadata: {},
  error_msg: 'Credential definition identifier is not set in proposal',
  initiator: 'self',
  parent_thread_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
  raw_credential: {
    cred_def_id: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
    rev_reg: {},
    rev_reg_id:
      'WgWxqztrNooG92RXvxSTWv:4:WgWxqztrNooG92RXvxSTWv:3:CL:20:tag:CL_ACCUM:0',
    schema_id: 'WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0',
    signature: {},
    signature_correctness_proof: {},
    values: {
      additionalProp1: {
        encoded: '-1',
        raw: 'string',
      },
      additionalProp2: {
        encoded: '-1',
        raw: 'string',
      },
      additionalProp3: {
        encoded: '-1',
        raw: 'string',
      },
    },
    witness: {},
  },
  revoc_reg_id: 'string',
  revocation_id: 'string',
  role: 'issuer',
  schema_id: 'WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0',
  state: 'credential_acked',
  thread_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
  trace: true,
  updated_at: '2021-12-31T23:59:59Z',
};

export default {
  credential,
  credentials,
  sendOffer,
};
