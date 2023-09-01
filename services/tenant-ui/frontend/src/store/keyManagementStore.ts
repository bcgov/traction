// Types
import {
  TenantAuthenticationApiRecord,
  TenantApiKeyRequest,
  TenantAuthenticationsApiResponse,
} from '@/types/acapyApi/acapyInterface';

import { defineStore } from 'pinia';
import { ref, Ref } from 'vue';
import { useAcapyApi } from './acapyApi';
import { fetchList } from './utils/fetchList.js';
import { API_PATH } from '@/helpers/constants';

export const useKeyManagementStore = defineStore('keyManagement', () => {
  const acapyApi = useAcapyApi();

  // state
  const apiKeys: Ref<TenantAuthenticationApiRecord[]> = ref([]);
  const loading: any = ref(false);
  const error: any = ref(null);

  // getters

  // actions
  async function listApiKeys() {
    return fetchList(
      `${API_PATH.TENANT_AUTHENTICATIONS_API}`,
      apiKeys,
      error,
      loading
    );
  }

  // Create an API key
  async function createApiKey(payload: TenantApiKeyRequest) {
    error.value = null;
    loading.value = true;

    let createResponse: TenantAuthenticationsApiResponse | undefined;
    try {
      createResponse = (
        await acapyApi.postHttp(
          API_PATH.TENANT_AUTHENTICATIONS_API_POST,
          payload
        )
      ).data;
      // Reload the keys list after updating
      await listApiKeys();
    } catch (err: any) {
      error.value = err;
    } finally {
      loading.value = false;
    }

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }

    // return the key
    return createResponse;
  }

  // Delete an API Key
  async function deleteApiKey(id: string) {
    loading.value = true;
    try {
      await acapyApi.deleteHttp(API_PATH.TENANT_AUTHENTICATIONS_API_RECORD(id));
      listApiKeys();
    } catch (err: any) {
      error.value = err;
    } finally {
      loading.value = false;
    }
    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
  }

  return { apiKeys, loading, createApiKey, deleteApiKey, listApiKeys };
});
