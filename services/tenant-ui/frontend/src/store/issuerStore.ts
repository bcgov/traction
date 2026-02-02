import {
  RevocationModuleResponse,
  RevokeRequest,
  V20CredExRecordDetail,
} from '@/types/acapyApi/acapyInterface';

import { defineStore } from 'pinia';
import { Ref, ref } from 'vue';
import { useAcapyApi } from './acapyApi';
import { useTenantStore } from './tenantStore';
import { fetchItem } from './utils/fetchItem';
import { fetchList } from './utils/fetchList.js';
import { API_PATH } from '@/helpers/constants';

export const useIssuerStore = defineStore('issuer', () => {
  const acapyApi = useAcapyApi();
  const tenantStore = useTenantStore();

  // state
  const credentials: Ref<V20CredExRecordDetail[]> = ref([]);
  const selectedCredential: any = ref(null);
  const loading: any = ref(false);
  const error: any = ref(null);

  // getters

  // actions

  async function listCredentials() {
    selectedCredential.value = null;
    return fetchList(
      `${API_PATH.ISSUE_CREDENTIAL_20_RECORDS}?role=issuer`,
      credentials,
      error,
      loading
    );
  }

  async function offerCredential(payload: any = {}) {
    console.log('> issuerStore.offerCredential');
    error.value = null;
    loading.value = true;

    let result = null;

    await acapyApi
      .postHttp(API_PATH.ISSUE_CREDENTIALS_20_SEND_OFFER, payload)
      .then((res) => {
        result = res.data.item;
        console.log(result);
      })
      .then(() => {
        listCredentials();
      })
      .catch((err) => {
        error.value = err;
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< issuerStore.offerCredential');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return result;
  }

  async function getCredential(id: string, params: any = {}) {
    const getloading: any = ref(false);
    return fetchItem(
      API_PATH.ISSUE_CREDENTIAL_20_RECORDS,
      id,
      error,
      getloading,
      params
    );
  }

  async function revokeCredential(payload?: RevokeRequest) {
    error.value = null;
    loading.value = true;

    try {
      // Determine which endpoint to use based on wallet type
      let walletType: string | undefined;
      if (!tenantStore.tenantWallet?.value) {
        try {
          const wallet = await tenantStore.getTenantSubWallet();
          walletType = wallet?.settings?.['wallet.type'];
        } catch (_err) {
          walletType = undefined;
        }
      } else {
        walletType = tenantStore.tenantWallet.value?.settings?.['wallet.type'];
      }

      // For askar-anoncreds wallets, use AnonCreds endpoint
      // For other wallets (askar, etc.), use Indy endpoint
      const useAnonCredsEndpoint = walletType === 'askar-anoncreds';

      const revocationEndpoint = useAnonCredsEndpoint
        ? API_PATH.ANONCREDS_REVOCATION_REVOKE
        : API_PATH.REVOCATION_REVOKE;

      let result: RevocationModuleResponse | null = null;

      try {
        const res = await acapyApi.postHttp(revocationEndpoint, payload);
        // AnonCreds endpoint returns {} (empty object), Indy returns { item: {...} }
        result = res.data.item || res.data;

        // Refresh the list to get the updated state from the backend
        await listCredentials();
      } catch (err) {
        error.value = err;
        throw err;
      }

      if (error.value != null) {
        const errToThrow = error.value;
        throw errToThrow;
      }
      return result;
    } catch (err) {
      if (error.value == null) {
        error.value = err as any;
      }
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deleteCredentialExchange(credExchangeId: string) {
    console.log('> connectionStore.deleteCredential');

    error.value = null;
    loading.value = true;

    let result = null;

    await acapyApi
      .deleteHttp(API_PATH.ISSUE_CREDENTIAL_20_RECORD(credExchangeId))
      .then((res) => {
        result = res.data.item;
      })
      .then(() => {
        listCredentials(); // Refresh table
      })
      .catch((err) => {
        error.value = err;
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< connectionStore.deleteCredential');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return result;
  }

  return {
    credentials,
    selectedCredential,
    loading,
    error,
    listCredentials,
    offerCredential,
    getCredential,
    revokeCredential,
    deleteCredentialExchange,
  };
});

export default {
  useIssuerStore,
};
