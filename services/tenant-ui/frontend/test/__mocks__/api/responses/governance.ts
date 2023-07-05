const listStoredSchemas = {
  results: [
    {
      schema_id: 'BRgEW8XcaTZQkoDXZqWLmP:2:Test Schema:1.0',
      schema: {
        ver: '1.0',
        id: 'BRgEW8XcaTZQkoDXZqWLmP:2:Test Schema:1.0',
        name: 'Test Schema',
        version: '1.0',
        attrNames: ['age'],
        seqNo: 867405,
      },
      updated_at: '2023-06-30T16:07:27.584504Z',
      created_at: '2023-06-30T16:07:27.584504Z',
    },
  ],
};

const createResponse = {
  sent: {
    schema_id: 'BRgEW8XcaTZQkoDXZqWLmP:2:Test Schema:1.0',
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
        schema_id: 'BRgEW8XcaTZQkoDXZqWLmP:2:Test Schema:1.0',
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

export default {
  listStoredSchemas,
  createResponse,
};
