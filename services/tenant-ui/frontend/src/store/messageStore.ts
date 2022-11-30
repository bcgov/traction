import { ref } from 'vue';
import { defineStore } from 'pinia';
import { useAcapyApi } from './acapyApi';
import { fetchListFromAPI } from './utils';

export const useMessageStore = defineStore('messages', () => {
  const messages: any = ref(null);
  const selectedMessage: any = ref(null);
  const loading: any = ref(false);
  const error: any = ref(null);

  // grab the tenant api
  const acapyApi = useAcapyApi();

  async function listMessages() {
    return fetchListFromAPI(
      acapyApi,
      '/basicmessages',
      messages,
      error,
      loading,
      {},
      true
    );
  }

  type SendPayload = {
    content: string;
  };

  async function sendMessage(connId: string, payload: SendPayload) {
    console.log('> messageStore.sendMessage');
    error.value = null;
    loading.value = true;

    let result = null;

    await acapyApi
      .postHttp(`/connections/${connId}/send-message`, payload)
      .then((res) => {
        console.log(res);
        result = res.data.item;
        console.log(result);
      })
      .catch((err) => {
        error.value = err;
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< messageStore.sendMessage');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return result;
  }

  return {
    messages,
    selectedMessage,
    loading,
    error,
    listMessages,
    sendMessage,
  };
});

export default {
  useMessageStore,
};
