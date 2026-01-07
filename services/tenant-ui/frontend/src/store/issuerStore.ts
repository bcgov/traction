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

  async function revokeCredential(
    payload: RevokeRequest,
    isAnonCredsCredential?: boolean
  ) {
    console.log('> issuerStore.revokeCredential');
    error.value = null;
    loading.value = true;

    try {
      // Determine which endpoint to use based on credential format
      // If format is not specified, fall back to wallet type
      let useAnonCredsEndpoint = isAnonCredsCredential;

      // If credential format is not explicitly detected (undefined), check wallet type
      if (useAnonCredsEndpoint === undefined) {
        // Ensure wallet is loaded and get wallet type
        let walletType: string | undefined;
        if (!tenantStore.tenantWallet?.value) {
          const wallet = await tenantStore.getTenantSubWallet();
          walletType = wallet?.settings?.['wallet.type'];
        } else {
          walletType =
            tenantStore.tenantWallet.value?.settings?.['wallet.type'];
        }

        // For askar-anoncreds wallets, default to AnonCreds endpoint
        // For other wallets, default to Indy endpoint
        useAnonCredsEndpoint = walletType === 'askar-anoncreds';

        console.log(
          'Credential format not detected, using wallet type:',
          walletType,
          '-> useAnonCredsEndpoint:',
          useAnonCredsEndpoint
        );
      } else {
        console.log(
          'Using explicit credential format detection:',
          isAnonCredsCredential
        );
      }

      const revocationEndpoint = useAnonCredsEndpoint
        ? API_PATH.ANONCREDS_REVOCATION_REVOKE
        : API_PATH.REVOCATION_REVOKE;

      console.log(
        'Using endpoint:',
        revocationEndpoint,
        'for AnonCreds credential:',
        useAnonCredsEndpoint
      );

      let result: RevocationModuleResponse | null = null;

      await acapyApi
        .postHttp(revocationEndpoint, payload)
        .then(async (res) => {
          // AnonCreds endpoint returns {} (empty object), Indy returns { item: {...} }
          result = res.data.item || res.data;

          // Refresh credentials to get updated state
          await listCredentials();

          // For AnonCreds endpoint, verify the revocation actually succeeded
          // The endpoint might return success but not actually revoke (e.g., Indy credential in AnonCreds wallet)
          if (useAnonCredsEndpoint && isAnonCredsCredential === undefined) {
            // Wait a moment for state to update, then verify
            await new Promise((resolve) => setTimeout(resolve, 500));
            await listCredentials();

            // Check if the credential was actually revoked by looking for it in the list
            // If credential format wasn't detected, the revocation might have failed silently
            console.log('Verifying revocation succeeded...');
            // Note: We can't easily verify here without the cred_ex_id, but the refresh will show the state
          }
        })
        .catch((err) => {
          error.value = err;
          // If we got a 500 error, the revocation might have still succeeded
          // (e.g., error in notification or response serialization after revocation)
          // Refresh the credential list to check the actual state
          if (err?.response?.status === 500) {
            console.log(
              'Got 500 error, refreshing credential list to check if revocation succeeded...'
            );
            listCredentials();
          }
        });

      console.log('< issuerStore.revokeCredential');

      if (error.value != null) {
        // throw error so $onAction.onError listeners can add their own handler
        const errToThrow = error.value;
        throw errToThrow;
      }
      // return data so $onAction.after listeners can add their own handler
      return result;
    } catch (err) {
      // Catch any errors that occur outside the promise chain (e.g., in wallet type check)
      // or when re-throwing error.value from the promise chain
      if (error.value == null) {
        error.value = err as any;
      }
      throw err;
    } finally {
      // Always reset loading, regardless of success or error
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
