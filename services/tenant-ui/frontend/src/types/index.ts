// import { IndyCredInfo, V10CredentialExchange } from '@/types/acapyApi/acapyInterface';
// export interface CombinedCredentialAndExchange {
//   credential?: IndyCredInfo;
//   credentialExchange: V10CredentialExchange;
// }

import { Ref } from 'vue';
import {
  CredDefStorageRecord,
  SchemaStorageRecord,
} from './acapyApi/acapyInterface';

export interface GetItem {
  item?: any;
  error?: Ref<String>;
  loading: boolean;
  fetchItem: (id?: string, params?: any) => Promise<void>;
}

export interface StoredSchemaWithCredDefs extends SchemaStorageRecord {
  credentialDefinitions: CredDefStorageRecord[];
}

export interface Attribute {
  name: string;
}

export interface AddSchemaFromLedgerRequest {
  schema_id: string;
}
