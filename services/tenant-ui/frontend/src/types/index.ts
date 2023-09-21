// import { IndyCredInfo, V10CredentialExchange } from '@/types/acapyApi/acapyInterface';
// export interface CombinedCredentialAndExchange {
//   credential?: IndyCredInfo;
//   credentialExchange: V10CredentialExchange;
// }

import { Ref } from 'vue';

export interface GetItem {
  item?: any;
  error?: Ref<String>;
  loading: boolean;
  fetchItem: (id?: string, params?: any) => Promise<void>;
}
