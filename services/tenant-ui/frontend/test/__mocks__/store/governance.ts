import { vi } from 'vitest';
import { StoredSchemaWithCredDefs } from '@/types';
import { CredDefStorageRecord } from '@/types/acapyApi/acapyInterface';
import { SchemaStorageRecord } from '@/types';

const credDefs: CredDefStorageRecord[] = [
  {
    created_at: '2023-10-04T17:04:41.339117Z',
    updated_at: '2023-10-04T17:04:41.339117Z',
    cred_def_id: 'TLuLqAw9aUKZoHmj67cLaa:3:CL:83929:AB',
    schema_id: 'TLuLqAw9aUKZoHmj67cLaa:2:passport:1.0',
    support_revocation: false,
    tag: 'AB',
  },
];

const schemaList: StoredSchemaWithCredDefs[] = [
  {
    schema: {
      name: 'age',
      version: '1.0',
      attrNames: ['age'],
    },
    schema_id: 'test-schema-id',
    created_at: '2023-07-04T17:16:13.771616Z',
    credentialDefinitions: credDefs,
  },
  {
    schema: {
      name: 'age',
      version: '1.0',
      attrNames: ['age'],
    },
    schema_id: 'test-schema-id',
    created_at: '2023-07-04T17:16:13.771616Z',
    credentialDefinitions: credDefs,
  },
];

const schemaStorageRecord: SchemaStorageRecord = {
  schema: {
    name: 'age',
    version: '1.0',
    attrNames: ['age'],
  },
  schema_id: 'test-schema-id',
  created_at: '2023-07-04T17:16:13.771616Z',
};

const store: { [key: string]: any } = {
  schemaList: {
    value: schemaList,
  },
  storedCredDefs: {
    value: credDefs,
  },
  listStoredSchemas: vi.fn(() => []),
  listStoredCredentialDefinitions: vi.fn(() => []),
};

export { store };
