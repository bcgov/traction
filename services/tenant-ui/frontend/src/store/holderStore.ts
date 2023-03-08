import {
  IndyCredInfo,
  V10CredentialExchange,
} from '@/types/acapyApi/acapyInterface';

import { defineStore } from 'pinia';
import { computed, Ref, ref } from 'vue';
import { fetchItem } from './utils/fetchItem';
import { fetchList } from './utils/fetchList.js';
import { useAcapyApi } from './acapyApi';
import { API_PATH } from '@/helpers/constants';

export const useHolderStore = defineStore('holder', () => {
  // state
  const credentials: Ref<IndyCredInfo[]> = ref([]);
  const credentialExchanges: Ref<V10CredentialExchange[]> = ref([]);
  const selectedCredential: any = ref(null);
  const presentations: any = ref(null);
  const selectedPresentation: any = ref(null);
  const loading: any = ref(false);
  const error: any = ref(null);

  // getters
  // const combinedCredentials = computed(() => {
  //   return credentialExchanges.value.map((ex) => {
  //     return {
  //       credentialExchange: ex,
  //       credential: credentials.value.find(c => c.),
  //     };
  //   });
  // });

  // actions

  async function listCredentials() {
    selectedCredential.value = null;
    return fetchList(API_PATH.CREDENTIALS, credentials, error, loading);
  }

  async function listHolderCredentialExchanges() {
    selectedCredential.value = null;
    return fetchList(
      API_PATH.ISSUE_CREDENTIAL_RECORDS,
      credentialExchanges,
      error,
      loading,
      { role: 'holder' }
    );
  }

  async function listPresentations() {
    selectedPresentation.value = null;
    return fetchList(
      API_PATH.HOLDER_PRESENTATIONS,
      presentations,
      error,
      loading
    );
  }

  async function getCredential(id: string, params: any = {}) {
    const getloading: any = ref(false);
    return fetchItem(API_PATH.CREDENTIALS, id, error, getloading, params);
  }

  async function getPresentation(id: string, params: any = {}) {
    const getloading: any = ref(false);
    return fetchItem(
      API_PATH.HOLDER_PRESENTATIONS,
      id,
      error,
      getloading,
      params
    );
  }

  const acapyApi = useAcapyApi();

  async function acceptCredentialOffer(credId: string) {
    console.log('> holderStore.acceptCredentialOffer');

    error.value = null;
    loading.value = true;

    const result = null;

    // await acapyApi
    //   .postHttp(API_PATH.HOLDER_CREDENTIALS_ACCEPT_OFFER(credId), {
    //     holder_credential_id: credId,
    //   })
    //   .then((res) => {
    //     result = res.data.item;
    //   })
    //   .then(() => {
    //     console.log('credential offer accepted.');
    //     listCredentials(); // Refresh table
    //   })
    //   .catch((err) => {
    //     error.value = err;
    //   })
    //   .finally(() => {
    //     loading.value = false;
    //   });
    // if (error.value != null) {
    //   // throw error so $onAction.onError listeners can add their own handler
    //   throw error.value;
    // }
    // return data so $onAction.after listeners can add their own handler
    return result;
  }

  async function rejectCredentialOffer(credId: string) {
    console.log('> holderStore.rejectCredentialOffer');

    error.value = null;
    loading.value = true;

    const result = null;

    // await acapyApi
    //   .postHttp(API_PATH.HOLDER_CREDENTIALS_REJECT_OFFER(credId), {
    //     holder_credential_id: credId,
    //   })
    //   .then((res) => {
    //     result = res.data.item;
    //   })
    //   .then(() => {
    //     console.log('credential offer rejected.');
    //     listCredentials(); // Refresh table
    //   })
    //   .catch((err) => {
    //     error.value = err;
    //   })
    //   .finally(() => {
    //     loading.value = false;
    //   });
    // if (error.value != null) {
    //   // throw error so $onAction.onError listeners can add their own handler
    //   throw error.value;
    // }
    // return data so $onAction.after listeners can add their own handler
    return result;
  }

  async function deleteHolderCredential(credId: string) {
    console.log('> holderStore.deleteHolderCredential');

    error.value = null;
    loading.value = true;

    const result = null;

    // await acapyApi
    //   .deleteHttp(API_PATH.HOLDER_CREDENTIAL(credId))
    //   .then((res) => {
    //     result = res.data.item;
    //   })
    //   .then(() => {
    //     console.log('credential deleted.');
    //     listCredentials(); // Refresh table
    //   })
    //   .catch((err) => {
    //     error.value = err;
    //   })
    //   .finally(() => {
    //     loading.value = false;
    //   });
    // if (error.value != null) {
    //   // throw error so $onAction.onError listeners can add their own handler
    //   throw error.value;
    // }
    // return data so $onAction.after listeners can add their own handler
    return result;
  }

  return {
    credentials,
    credentialExchanges,
    presentations,
    selectedCredential,
    selectedPresentation,
    loading,
    error,
    listCredentials,
    listHolderCredentialExchanges,
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
