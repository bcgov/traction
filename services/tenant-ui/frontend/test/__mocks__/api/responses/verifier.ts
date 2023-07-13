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

const presentProofSendRequest = {
  auto_present: false,
  auto_verify: true,
  connection_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
  created_at: '2021-12-31T23:59:59Z',
  error_msg: 'Invalid structure',
  initiator: 'self',
  presentation: {
    identifiers: [
      {
        cred_def_id: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
        rev_reg_id:
          'WgWxqztrNooG92RXvxSTWv:4:WgWxqztrNooG92RXvxSTWv:3:CL:20:tag:CL_ACCUM:0',
        schema_id: 'WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0',
        timestamp: 1640995199,
      },
    ],
    proof: {
      aggregated_proof: {
        c_hash: 'string',
        c_list: [[0]],
      },
      proofs: [
        {
          non_revoc_proof: {
            c_list: {
              additionalProp1: 'string',
              additionalProp2: 'string',
              additionalProp3: 'string',
            },
            x_list: {
              additionalProp1: 'string',
              additionalProp2: 'string',
              additionalProp3: 'string',
            },
          },
          primary_proof: {
            eq_proof: {
              a_prime: '0',
              e: '0',
              m: {
                additionalProp1: '0',
                additionalProp2: '0',
                additionalProp3: '0',
              },
              m2: '0',
              revealed_attrs: {
                additionalProp1: '-1',
                additionalProp2: '-1',
                additionalProp3: '-1',
              },
              v: '0',
            },
            ge_proofs: [
              {
                alpha: '0',
                mj: '0',
                predicate: {
                  attr_name: 'string',
                  p_type: 'LT',
                  value: 0,
                },
                r: {
                  additionalProp1: '0',
                  additionalProp2: '0',
                  additionalProp3: '0',
                },
                t: {
                  additionalProp1: '0',
                  additionalProp2: '0',
                  additionalProp3: '0',
                },
                u: {
                  additionalProp1: '0',
                  additionalProp2: '0',
                  additionalProp3: '0',
                },
              },
            ],
          },
        },
      ],
    },
    requested_proof: {
      predicates: {
        additionalProp1: {
          sub_proof_index: 0,
        },
        additionalProp2: {
          sub_proof_index: 0,
        },
        additionalProp3: {
          sub_proof_index: 0,
        },
      },
      revealed_attr_groups: {
        additionalProp1: {
          sub_proof_index: 0,
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
        },
        additionalProp2: {
          sub_proof_index: 0,
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
        },
        additionalProp3: {
          sub_proof_index: 0,
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
        },
      },
      revealed_attrs: {
        additionalProp1: {
          encoded: '-1',
          raw: 'string',
          sub_proof_index: 0,
        },
        additionalProp2: {
          encoded: '-1',
          raw: 'string',
          sub_proof_index: 0,
        },
        additionalProp3: {
          encoded: '-1',
          raw: 'string',
          sub_proof_index: 0,
        },
      },
      self_attested_attrs: {},
      unrevealed_attrs: {},
    },
  },
  presentation_exchange_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
  presentation_proposal_dict: {
    '@id': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    '@type': 'https://didcomm.org/my-family/1.0/my-message-type',
    comment: 'string',
    presentation_proposal: {
      '@type':
        'did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/present-proof/1.0/presentation-preview',
      attributes: [
        {
          cred_def_id: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
          'mime-type': 'image/jpeg',
          name: 'favourite_drink',
          referent: '0',
          value: 'martini',
        },
      ],
      predicates: [
        {
          cred_def_id: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
          name: 'high_score',
          predicate: '>=',
          threshold: 0,
        },
      ],
    },
  },
  presentation_request: {
    name: 'Proof request',
    non_revoked: {
      from: 1640995199,
      to: 1640995199,
    },
    nonce: '1',
    requested_attributes: {
      additionalProp1: {
        name: 'favouriteDrink',
        names: ['age'],
        non_revoked: {
          from: 1640995199,
          to: 1640995199,
        },
        restrictions: [
          {
            additionalProp1: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
            additionalProp2: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
            additionalProp3: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
          },
        ],
      },
      additionalProp2: {
        name: 'favouriteDrink',
        names: ['age'],
        non_revoked: {
          from: 1640995199,
          to: 1640995199,
        },
        restrictions: [
          {
            additionalProp1: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
            additionalProp2: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
            additionalProp3: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
          },
        ],
      },
      additionalProp3: {
        name: 'favouriteDrink',
        names: ['age'],
        non_revoked: {
          from: 1640995199,
          to: 1640995199,
        },
        restrictions: [
          {
            additionalProp1: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
            additionalProp2: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
            additionalProp3: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
          },
        ],
      },
    },
    requested_predicates: {
      additionalProp1: {
        name: 'index',
        non_revoked: {
          from: 1640995199,
          to: 1640995199,
        },
        p_type: '>=',
        p_value: 0,
        restrictions: [
          {
            additionalProp1: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
            additionalProp2: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
            additionalProp3: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
          },
        ],
      },
      additionalProp2: {
        name: 'index',
        non_revoked: {
          from: 1640995199,
          to: 1640995199,
        },
        p_type: '>=',
        p_value: 0,
        restrictions: [
          {
            additionalProp1: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
            additionalProp2: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
            additionalProp3: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
          },
        ],
      },
      additionalProp3: {
        name: 'index',
        non_revoked: {
          from: 1640995199,
          to: 1640995199,
        },
        p_type: '>=',
        p_value: 0,
        restrictions: [
          {
            additionalProp1: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
            additionalProp2: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
            additionalProp3: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
          },
        ],
      },
    },
    version: '1.0',
  },
  presentation_request_dict: {
    '@id': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    '@type': 'https://didcomm.org/my-family/1.0/my-message-type',
    comment: 'string',
    'request_presentations~attach': [
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
  role: 'prover',
  state: 'verified',
  thread_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
  trace: true,
  updated_at: '2021-12-31T23:59:59Z',
  verified: 'true',
  verified_msgs: ['string'],
};

export default {
  presentProofRecords,
  presentProofSendRequest,
};
