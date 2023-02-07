import { defineStore } from 'pinia';
import { ref } from 'vue';
import { fetchList } from './utils/fetchList.js';
import { useTenantApi } from './tenantApi';
import { fetchItem } from './utils/fetchItem';
import { API_PATH } from '@/helpers/constants';

export const useIssuerStore = defineStore('issuer', () => {
  const tenantApi = useTenantApi();

  // state
  const credentials: any = ref(null);
  const selectedCredential: any = ref(null);
  const loading: any = ref(false);
  const error: any = ref(null);

  // getters

  // actions

  async function listCredentials() {
    selectedCredential.value = null;
    return fetchList(
      `${API_PATH.ISSUE_CREDENTIALS_RECORDS}?role=issuer`,
      credentials,
      error,
      loading
    );
  }

  async function offerCredential(payload: any = {}) {
    console.log('> issuerStore.createSchemaTemplate');
    error.value = null;
    loading.value = true;

    let result = null;

    await tenantApi
      .postHttp(API_PATH.ISSUER_CREDENTIALS, payload)
      .then((res) => {
        console.log(res);
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
    console.log('< issuerStore.createSchemaTemplate');

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
      API_PATH.ISSUER_CREDENTIALS,
      id,
      error,
      getloading,
      params
    );
  }

  async function revokeCredential(payload: any = {}) {
    console.log('> issuerStore.revokeCredential');
    error.value = null;
    loading.value = true;

    let result = null;

    await tenantApi
      .postHttp(
        API_PATH.ISSUER_CREDENTIAL_REVOKE(payload.issuer_credential_id),
        payload
      )
      .then((res) => {
        result = res.data.item;
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
    console.log('< issuerStore.revokeCredential');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return result;
  }

  async function deleteCredential(issuerCredentialId: string) {
    console.log('> contactsStore.deleteCredential');

    error.value = null;
    loading.value = true;

    let result = null;

    await tenantApi
      .deleteHttp(API_PATH.ISSUER_CREDENTIAL(issuerCredentialId))
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
    console.log('< contactsStore.deleteCredential');

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
    deleteCredential,
  };
});

export default {
  useIssuerStore,
};
