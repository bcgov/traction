import { defineStore } from 'pinia';
import { ref } from 'vue';
import { fetchList } from './utils/fetchList.js';

export const useIssuerStore = defineStore('issuer', () => {
  // state
  const credentials: any = ref(null);
  const selectedCredential: any = ref(null);
  const loading: any = ref(false);
  const error: any = ref(null);

  // getters

  // actions

  async function listCredentials() {
    selectedCredential.value = null;
    return fetchList('/tenant/v1/issuer/credentials/', credentials, error, loading);
  }

  return { credentials, selectedCredential, loading, error, listCredentials };
});

export default {
  useIssuerStore,
};
