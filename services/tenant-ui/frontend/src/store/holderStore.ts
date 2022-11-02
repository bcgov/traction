import { defineStore } from 'pinia';
import { ref } from 'vue';
import { fetchItem } from './utils/fetchItem';
import { fetchList } from './utils/fetchList.js';
import { useTenantApi } from './tenantApi';

export const useHolderStore = defineStore('holder', () => {
  // state
  const credentials: any = ref(null);
  const selectedCredential: any = ref(null);
  const presentations: any = ref(null);
  const selectedPresentation: any = ref(null);
  const loading: any = ref(false);
  const error: any = ref(null);

  // getters

  // actions

  async function listCredentials() {
    selectedCredential.value = null;
    return fetchList(
      '/tenant/v1/holder/credentials/',
      credentials,
      error,
      loading
    );
  }

  async function listPresentations() {
    selectedPresentation.value = null;
    return fetchList(
      '/tenant/v1/holder/presentations/',
      presentations,
      error,
      loading
    );
  }

  async function getCredential(id: string, params: any = {}) {
    const getloading: any = ref(false);
    return fetchItem(
      '/tenant/v1/holder/credentials/',
      id,
      error,
      getloading,
      params
    );
  }

  async function getPresentation(id: string, params: any = {}) {
    const getloading: any = ref(false);
    return fetchItem(
      '/tenant/v1/holder/presentations/',
      id,
      error,
      getloading,
      params
    );
  }

  const tenantApi = useTenantApi();

  async function acceptCredentialOffer(credId: string) {
    console.log('> holderStore.acceptCredentialOffer');

    error.value = null;
    loading.value = true;

    let result = null;

    await tenantApi
      .postHttp(`/tenant/v1/holder/credentials/${credId}/accept-offer`, {
        holder_credential_id: credId,
      })
      .then((res) => {
        result = res.data.item;
      })
      .then(() => {
        console.log('credential offer accepted.');
        listCredentials(); // Refresh table
      })
      .catch((err) => {
        error.value = err;
      })
      .finally(() => {
        loading.value = false;
      });
    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return result;
  }

  async function rejectCredentialOffer(credId: string) {
    console.log('> holderStore.rejectCredentialOffer');

    error.value = null;
    loading.value = true;

    let result = null;

    await tenantApi
      .postHttp(`/tenant/v1/holder/credentials/${credId}/reject-offer`, {
        holder_credential_id: credId,
      })
      .then((res) => {
        result = res.data.item;
      })
      .then(() => {
        console.log('credential offer rejected.');
        listCredentials(); // Refresh table
      })
      .catch((err) => {
        error.value = err;
      })
      .finally(() => {
        loading.value = false;
      });
    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return result;
  }

  async function deleteHolderCredential(credId: string) {
    console.log('> holderStore.deleteHolderCredential');

    error.value = null;
    loading.value = true;

    let result = null;

    await tenantApi
      .deleteHttp(`/tenant/v1/holder/credentials/${credId}`)
      .then((res) => {
        result = res.data.item;
      })
      .then(() => {
        console.log('credential deleted.');
        listCredentials(); // Refresh table
      })
      .catch((err) => {
        error.value = err;
      })
      .finally(() => {
        loading.value = false;
      });
    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return result;
  }

  return {
    credentials,
    presentations,
    selectedCredential,
    selectedPresentation,
    loading,
    error,
    listCredentials,
    listPresentations,
    getCredential,
    getPresentation,
    acceptCredentialOffer,
    rejectCredentialOffer,
    deleteHolderCredential,
  };
});

export default {
  useHolderStore,
};
