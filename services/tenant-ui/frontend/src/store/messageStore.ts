import { ref, Ref } from 'vue';
import { defineStore } from 'pinia';
import { useAcapyApi } from './acapyApi';
import { fetchListFromAPI } from './utils';
import { API_PATH } from '@/helpers/constants';
import { BasicMessageRecord } from '@/types/acapyApi/acapyInterface';

/**
 * This is the interface for the message list.
 */
export interface Message {
  connection_id: string;
  content: string;
  created_at: string;
  message_id: string;
  sent_time: string;
  state: string;
  updated_at: string;
  displayTime: boolean;
}

export const useMessageStore = defineStore('messages', () => {
  const messages: Ref<Message[]> = ref([]);
  const selectedMessage: any = ref(null);
  const loading: any = ref(false);
  const error: any = ref(null);
  const newMessage: any = ref('');

  // grab the tenant api
  const acapyApi = useAcapyApi();

  async function listMessages(connId?: string) {
    /**
     * Default to empty object, but if a connection ID
     * is passed in, add it to the params.
     */
    let params = {};
    if (connId) params = { connection_id: connId };

    return fetchListFromAPI(
      acapyApi,
      API_PATH.BASICMESSAGES,
      messages,
      error,
      loading,
      params
    );
  }

  type SendPayload = {
    content: string;
  };

  async function sendMessage(connId: string, payload: SendPayload) {
    console.log('> messageStore.sendMessage');
    error.value = null;
    loading.value = true;
    newMessage.value = payload.content;

    let result = null;

    await acapyApi
      .postHttp(API_PATH.BASICMESSAGES_SEND(connId), payload)
      .then((res) => {
        result = res.data.item;
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
    newMessage,
    listMessages,
    sendMessage,
  };
});

export default {
  useMessageStore,
};
