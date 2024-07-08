// import { IndyCredInfo, V10CredentialExchange } from '@/types/acapyApi/acapyInterface';
// export interface CombinedCredentialAndExchange {
//   credential?: IndyCredInfo;
//   credentialExchange: V10CredentialExchange;
// }

import { Ref } from 'vue';
import {
  CredDefStorageRecord,
  SchemaStorageRecord as AcapySchemaStorageRecord,
  Schema,
  V20CredExRecordByFormat,
} from './acapyApi/acapyInterface';

export interface GetItem {
  item?: any;
  error?: Ref<String>;
  loading: boolean;
  fetchItem: (id?: string, params?: any) => Promise<void>;
}

export interface Attribute {
  name: string;
}

export interface AddSchemaFromLedgerRequest {
  schema_id: string;
}

// Extensions of things from the generated acapyInterface.ts types
// those come from an openAPI generator, and the ACA-Py API is not fully
// described in the openAPI spec for some things, so we extend some types
export interface StoredSchemaWithCredDefs extends SchemaStorageRecord {
  credentialDefinitions: CredDefStorageRecord[];
}
export interface SchemaStorageRecord extends AcapySchemaStorageRecord {
  schema: Schema;
}
// The Types in the cred exchange format are just "object"
export interface ExtendedV20CredExRecordByFormat
  extends V20CredExRecordByFormat {
  cred_offer?: {
    indy?: {
      cred_def_id?: string;
      schema_id?: string;
      key_correctness_proof?: any;
      nonce?: string;
    };
  };
}
