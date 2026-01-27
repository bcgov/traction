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

  async function revokeCredential(payload: RevokeRequest) {
    console.log('> issuerStore.revokeCredential');
    error.value = null;
    loading.value = true;

    try {
      // Determine which endpoint to use based on wallet type
      let walletType: string | undefined;
      if (!tenantStore.tenantWallet?.value) {
        try {
          const wallet = await tenantStore.getTenantSubWallet();
          walletType = wallet?.settings?.['wallet.type'];
          if (!walletType && wallet) {
            console.warn(
              'Wallet retrieved but wallet.type setting not found, defaulting to Indy endpoint'
            );
          }
        } catch (err) {
          console.error(
            'Failed to retrieve tenant wallet, defaulting to Indy endpoint:',
            err
          );
          walletType = undefined;
        }
      } else {
        walletType = tenantStore.tenantWallet.value?.settings?.['wallet.type'];
      }

      // For askar-anoncreds wallets, use AnonCreds endpoint
      // For other wallets (askar, etc.), use Indy endpoint
      const useAnonCredsEndpoint = walletType === 'askar-anoncreds';

      console.log(
        'Using wallet type:',
        walletType,
        '-> useAnonCredsEndpoint:',
        useAnonCredsEndpoint
      );

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

      try {
        await acapyApi
          .postHttp(revocationEndpoint, payload)
          .then(async (res) => {
            // AnonCreds endpoint returns {} (empty object), Indy returns { item: {...} }
            result = res.data.item || res.data;

            // Directly update the credential state in the store
            // Find the credential by cred_ex_id or rev_reg_id/cred_rev_id
            const credExId = payload.cred_ex_id;
            const revRegId = payload.rev_reg_id;
            const credRevId = payload.cred_rev_id;

            if (credExId) {
              // Update by credential exchange ID
              const credentialIndex = credentials.value.findIndex(
                (cred) => cred.cred_ex_record?.cred_ex_id === credExId
              );
              if (credentialIndex !== -1) {
                // Update the state directly
                if (credentials.value[credentialIndex].cred_ex_record) {
                  credentials.value[credentialIndex].cred_ex_record.state =
                    'credential-revoked';
                }
              }
            } else if (revRegId && credRevId) {
              // Update by revocation registry ID and credential revocation ID
              const credentialIndex = credentials.value.findIndex((cred) => {
                const indyMatch =
                  cred.indy?.rev_reg_id === revRegId &&
                  cred.indy?.cred_rev_id === credRevId;
                const anoncredsMatch =
                  cred.anoncreds?.rev_reg_id === revRegId &&
                  cred.anoncreds?.cred_rev_id === credRevId;
                return indyMatch || anoncredsMatch;
              });
              if (credentialIndex !== -1) {
                // Update the state directly
                if (credentials.value[credentialIndex].cred_ex_record) {
                  credentials.value[credentialIndex].cred_ex_record.state =
                    'credential-revoked';
                }
              }
            }

            // Refresh the list to ensure we have the latest data from the backend
            await listCredentials();
          })
          .catch((err) => {
            error.value = err;
            // If we got a 500 error, the revocation might have still succeeded
            // (e.g., error in notification or response serialization after revocation)
            // Refresh the credential list to check the actual state
            // Note: We don't await this to avoid overwriting the original error
            if (err?.response?.status === 500) {
              console.log(
                'Got 500 error, refreshing credential list to check if revocation succeeded...'
              );
              // Fire-and-forget: don't await to preserve the original error
              listCredentials().catch(() => {
                // Silently ignore errors from listCredentials to preserve original error
              });
            }
            // Re-throw to ensure the promise chain rejects
            throw err;
          });
      } catch (err) {
        // Catch any errors that escape the promise chain
        if (error.value == null) {
          error.value = err;
        }
        // Re-throw to be caught by outer catch block
        throw err;
      }

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
