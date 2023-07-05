const schemas = {
  results: [
    {
      schema_id: 'Test Schema:1.0',
      schema: {
        ver: '1.0',
        id: 'Test Schema:1.0',
        name: 'Test Schema',
        version: '1.0',
        attrNames: ['age'],
        seqNo: 867405,
      },
      state: 'active',
      updated_at: '2023-06-30T16:07:27.584504Z',
      created_at: '2023-06-30T16:07:27.584504Z',
      credential_templates: [],
    },
  ],
};

const createSchema = {
  sent: {
    schema_id: 'Test Schema:1.0',
    schema: {
      signed_txn:
        '{"endorser": "SVfHGCEEvEFmpBPcxgNqRR", "identifier": "BRgEW8XcaTZQkoDXZqWLmP", "operation": {"data": {"attr_names": ["age"], "name": "Test Schema", "version": "1.0"}, "type": "101"}, "protocolVersion": 2, "reqId": 1688141245264590604, "signature": "hJJKLUWNHP7MioxArJY3D6FAZpRadQo7LNTnHuEnrr3pMvmP7n1LbRpjdpHjzVAYBoN4NA2doDkUiAoJJeT3X16"}',
    },
  },
  txn: {
    transaction_id: '64e9e4af-96c3-4316-80dc-e4ef42768c28',
    state: 'request_sent',
    connection_id: '7dcfd983-71f9-4a05-a13b-a2026ed85bb9',
    _type: 'http://didcomm.org/sign-attachment/%VER/signature-request',
    messages_attach: [
      {
        '@id': '17230197-8871-4bb1-b130-04e25e37abab',
        'mime-type': 'application/json',
        data: {
          json: '{"endorser": "SVfHGCEEvEFmpBPcxgNqRR", "identifier": "BRgEW8XcaTZQkoDXZqWLmP", "operation": {"data": {"attr_names": ["age"], "name": "Test Schema", "version": "1.0"}, "type": "101"}, "protocolVersion": 2, "reqId": 1688141245264590604, "signature": "hJJKLUWNHP7MioxArJY3D6FAZpRadQo7LNTnHuEnrr3pMvmP7n1LbRpjdpHjzVAYBoN4NA2doDkUiAoJJeT3X16"}',
        },
      },
    ],
    trace: false,
    timing: {
      expires_time: null,
    },
    formats: [
      {
        attach_id: '17230197-8871-4bb1-b130-04e25e37abab',
        format: 'dif/endorse-transaction/request@v1.0',
      },
    ],
    meta_data: {
      context: {
        schema_id: 'Test Schema:1.0',
        schema_name: 'Test Schema',
        schema_version: '1.0',
        attributes: ['age'],
      },
      processing: {},
    },
    updated_at: '2023-06-30T16:07:25.288822Z',
    signature_request: [
      {
        context: 'did:sov',
        method: 'add-signature',
        signature_type: '<requested signature type>',
        signer_goal_code: 'aries.transaction.endorse',
        author_goal_code: 'aries.transaction.ledger.write',
      },
    ],
    signature_response: [],
    created_at: '2023-06-30T16:07:25.275310Z',
  },
};

const copySchema = {
  schema: {
    ver: '1.0',
    id: 'QZqhBmoV2XxrhpPrYDj5zN:2:Test Schema:1.0',
    name: 'Test Schema',
    version: '1.0',
    attrNames: ['age'],
    seqNo: 872882,
  },
  updated_at: '2023-07-05T16:13:57.687414Z',
  created_at: '2023-07-05T16:13:57.687414Z',
  schema_id: 'QZqhBmoV2XxrhpPrYDj5zN:2:Test Schema:1.0',
};

const deleteResponse = {
  success: true,
};

const credentialDefinitions = {
  results: [
    {
      created_at: '2021-12-31T23:59:59Z',
      cred_def_id: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
      rev_reg_size: 1000,
      schema_id: 'Test Schema:1.0',
      state: 'active',
      support_revocation: true,
      tag: 'default',
      updated_at: '2021-12-31T23:59:59Z',
    },
  ],
};

const createCredentialDefinition = {
  sent: {
    credential_definition_id: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
  },
  txn: {
    _type: '101',
    connection_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    created_at: '2021-12-31T23:59:59Z',
    endorser_write_txn: true,
    formats: [
      {
        attach_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
        format: 'dif/endorse-transaction/request@v1.0',
      },
    ],
    messages_attach: [
      {
        '@id': '143c458d-1b1c-40c7-ab85-4d16808ddf0a',
        data: {
          json: '{"endorser": "V4SGRU86Z58d6TV7PBUe6f","identifier": "LjgpST2rjsoxYegQDRm7EL","operation": {"data": {"attr_names": ["first_name", "last_name"],"name": "test_schema","version": "2.1",},"type": "101",},"protocolVersion": 2,"reqId": 1597766666168851000,"signatures": {"LjgpST2rjsox": "4ATKMn6Y9sTgwqaGTm7py2c2M8x1EVDTWKZArwyuPgjU"},"taaAcceptance": {"mechanism": "manual","taaDigest": "f50fe2c2ab977006761d36bd6f23e4c6a7e0fc2feb9f62","time": 1597708800,}}',
        },
        'mime-type': 'application/json',
      },
    ],
    meta_data: {
      context: {
        param1: 'param1_value',
        param2: 'param2_value',
      },
      post_process: [
        {
          topic: 'topic_value',
          other: 'other_value',
        },
      ],
    },
    signature_request: [
      {
        author_goal_code: 'aries.transaction.ledger.write',
        context: 'did:sov',
        method: 'add-signature',
        signature_type: '<requested signature type>',
        signer_goal_code: 'aries.transaction.endorse',
      },
    ],
    signature_response: [
      {
        context: 'did:sov',
        message_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
        method: 'add-signature',
        signer_goal_code: 'aries.transaction.refuse',
      },
    ],
    state: 'active',
    thread_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    timing: {
      expires_time: '2020-12-13T17:29:06+0000',
    },
    trace: true,
    transaction_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    updated_at: '2021-12-31T23:59:59Z',
  },
};

const credentialDefinition = {
  credential_definition: {
    id: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
    schemaId: 'Test Schema:1.0',
    tag: 'tag',
    type: 'CL',
    value: {
      primary: {
        n: '0',
        r: {
          master_secret: '0',
          number: '0',
          remainder: '0',
        },
        rctxt: '0',
        s: '0',
        z: '0',
      },
      revocation: {
        g: '1 1F14F&ECB578F 2 095E45DDF417D',
        g_dash: '1 1D64716fCDC00C 1 0C781960FA66E3D3 2 095E45DDF417D',
        h: '1 16675DAE54BFAE8 2 095E45DD417D',
        h0: '1 21E5EF9476EAF18 2 095E45DDF417D',
        h1: '1 236D1D99236090 2 095E45DDF417D',
        h2: '1 1C3AE8D1F1E277 2 095E45DDF417D',
        h_cap: '1 1B2A32CF3167 1 2490FEBF6EE55 1 0000000000000000',
        htilde: '1 1D8549E8C0F8 2 095E45DDF417D',
        pk: '1 142CD5E5A7DC 1 153885BD903312 2 095E45DDF417D',
        u: '1 0C430AAB2B4710 1 1CB3A0932EE7E 1 0000000000000000',
        y: '1 153558BD903312 2 095E45DDF417D 1 0000000000000000',
      },
    },
    ver: '1.0',
  },
};

const ocas = {
  results: [
    {
      bundle: {},
      created_at: '2021-12-31T23:59:59Z',
      cred_def_id: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
      oca_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
      owner_did: 'string',
      schema_id: 'WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0',
      state: 'active',
      updated_at: '2021-12-31T23:59:59Z',
      url: 'string',
    },
  ],
};

const oca = {
  bundle: {},
  created_at: '2021-12-31T23:59:59Z',
  cred_def_id: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
  oca_id: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
  owner_did: 'string',
  schema_id: 'WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0',
  state: 'active',
  updated_at: '2021-12-31T23:59:59Z',
  url: 'string',
};

const createOca = {
  bundle: {},
  cred_def_id: 'WgWxqztrNooG92RXvxSTWv:3:CL:20:tag',
  schema_id: 'WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0',
  url: 'string',
};

export default {
  copySchema,
  createCredentialDefinition,
  createOca,
  createSchema,
  credentialDefinition,
  credentialDefinitions,
  deleteResponse,
  oca,
  ocas,
  schemas,
};
