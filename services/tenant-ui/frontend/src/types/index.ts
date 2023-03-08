// import { IndyCredInfo, V10CredentialExchange } from '@/types/acapyApi/acapyInterface';
// export interface CombinedCredentialAndExchange {
//   credential?: IndyCredInfo;
//   credentialExchange: V10CredentialExchange;
// }

export interface GetItem {
  item?: any;
  loading: boolean;
  fetchItem: (id: string, params?: any) => Promise<void>;
}
