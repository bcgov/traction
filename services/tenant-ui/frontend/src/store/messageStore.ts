import { ref } from 'vue';
import { defineStore } from 'pinia';
import { useTenantApi } from './tenantApi';
import { fetchList, filterMapSortList, sortByLabelAscending } from './utils';
import { fetchItem } from './utils';
import axios from 'axios';

export const useMessageStore = defineStore('messages', () => {
  const messages: any = ref(null);
  const selectedMessage: any = ref(null);
  const loading: any = ref(false);
  const error: any = ref(null);

  // grab the tenant api
  const tenantApi = useTenantApi();

  async function listMessages() {
    return fetchList('/tenant/v1/messages/', messages, error, loading);
  }

  return {
    messages,
    selectedMessage,
    loading,
    error,
    listMessages,
  };
});

export default {
  useMessageStore,
};
