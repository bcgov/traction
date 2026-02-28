import {
  IndyCredInfo,
  V20CredExRecordDetail,
} from '@/types/acapyApi/acapyInterface';

import { defineStore } from 'pinia';
import { Ref, ref } from 'vue';
import { fetchItem } from './utils/fetchItem';
import { fetchList } from './utils/fetchList.js';
import { useAcapyApi } from './acapyApi';
import { API_PATH } from '@/helpers/constants';

export const useHolderStore = defineStore('holder', () => {
  const acapyApi = useAcapyApi();

  // state
  const credentials: Ref<IndyCredInfo[]> = ref([]);
  const credentialExchanges: Ref<V20CredExRecordDetail[]> = ref([]);
  const selectedCredential: any = ref(null);

  const presentations: any = ref(null);
  const selectedPresentation: any = ref(null);

  const loading: any = ref(false);
  const error: any = ref(null);

  // actions

  async function listCredentials() {
    return fetchList(API_PATH.CREDENTIALS, credentials, error, loading);
  }

  async function listHolderCredentialExchanges() {
    return fetchList(
      API_PATH.ISSUE_CREDENTIAL_20_RECORDS,
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

  async function acceptCredentialOffer(credExId: string) {
    console.log('> holderStore.acceptCredentialOffer');

    error.value = null;
    loading.value = true;

    let result = null;

    await acapyApi
      .postHttp(API_PATH.ISSUE_CREDENTIAL_20_RECORDS_SEND_REQUEST(credExId))
      .then((res) => {
        result = res.data.item;
      })
      .then(() => {
        console.log('credential offer accepted.');
        listHolderCredentialExchanges(); // Refresh table
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

  async function deleteCredentialExchange(credExId: string) {
    console.log('> holderStore.deleteCredentialExchange');

    error.value = null;
    loading.value = true;

    let result = null;

    await acapyApi
      .deleteHttp(API_PATH.ISSUE_CREDENTIAL_20_RECORD(credExId))
      .then((res) => {
        result = res.data.item;
      })
      .then(() => {
        console.log('credential exchange deleted.');
        listHolderCredentialExchanges(); // Refresh table
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

  async function sendProblemReport(credExId: string) {
    console.log('> holderStore.sendProblemReport');

    await acapyApi
      .postHttp(API_PATH.ISSUE_CREDENTIAL_20_RECORDS_PROBLEM_REPORT(credExId), {
        description: 'Tenant rejected credential offer through Tenant UI.',
      })
      .then(() => {
        console.log('Problem report sent.');
      });
  }

  return {
    credentialExchanges,
    credentials,
    error,
    loading,
    presentations,
    selectedCredential,
    selectedPresentation,
    acceptCredentialOffer,
    deleteCredentialExchange,
    getCredential,
    getPresentation,
    listCredentials,
    listHolderCredentialExchanges,
    listPresentations,
    sendProblemReport,
  };
});

export default {
  useHolderStore,
};
