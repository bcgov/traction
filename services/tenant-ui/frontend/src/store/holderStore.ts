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

  async function acceptCredentialOffer(cred_id: string) {
    await tenantApi
      .postHttp(`/tenant/v1/holder/credentials/${cred_id}/accept-offer`, {
        holder_credential_id: cred_id,
      })
      .then((res) => {
        console.log(res);
      });
  }

  async function rejectCredentialOffer(cred_id: string) {
    await tenantApi
      .postHttp(`/tenant/v1/holder/credentials/${cred_id}/reject-offer`, {
        holder_credential_id: cred_id,
      })
      .then((res) => {
        console.log(res);
      });
  }

  async function deleteHolderCredential(cred_id: string) {
    await tenantApi
      .deleteHttp(`/tenant/v1/holder/credentials/${cred_id}`)
      .then((res) => {
        console.log(res);
      });
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
    acceptCredentialOffer,
    rejectCredentialOffer,
    deleteHolderCredential,
  };
});

export default {
  useHolderStore,
};
