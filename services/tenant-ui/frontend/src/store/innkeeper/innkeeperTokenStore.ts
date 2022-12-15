import axios from 'axios';
import { defineStore, storeToRefs } from 'pinia';
import { computed, ref } from 'vue';
import { Ref } from 'vue';
import { API_PATH } from '@/helpers/constants';
import { useConfigStore } from '../configStore';
import { useTokenStore } from '../tokenStore';

export const useInnkeeperTokenStore = defineStore(
  'useInnkeeperTokenStore',
  () => {
    const { config } = storeToRefs(useConfigStore());
    const { acapyToken } = storeToRefs(useTokenStore());
    // A raw api call without using the interceptors from the acapyApiTenantStore
    const api = axios.create({
      baseURL: config.value.frontend.tenantProxyPath,
    });

    // state
    const loading: Ref<boolean> = ref(false);
    const error: Ref<string | null> = ref(null);

    // getters
    const innkeeperReady = computed((): boolean => {
      return acapyToken.value != null;
    });

    /**
     * The format of the token request is:
     */
    interface LoginParameters {
      adminName: string;
      adminKey: string;
    }

    // actions
    async function login(params: LoginParameters): Promise<string | null> {
      console.log('> innkeeperTokenStore.load');
      console.log('params', params);
      const payload = { wallet_key: params.adminKey };
      acapyToken.value = null;
      error.value = null;
      loading.value = true;

      // TODO: isolate this to something reusable when we grab an axios connection.
      await api
        .post(API_PATH.MULTITENANCY_TENANT_TOKEN(params.adminName), payload)
        .then((res) => {
          acapyToken.value = res.data.token;
        })
        .catch((err) => {
          error.value = err;
          console.log(error.value);
        })
        .finally(() => {
          loading.value = false;
        });
      console.log('< innkeeperTokenStore.load');

      if (error.value != null) {
        // throw error so $onAction.onError listeners can add their own handler
        throw error.value;
      }
      // return data so $onAction.after listeners can add their own handler
      return acapyToken.value;
    }

    function clearToken(): void {
      console.log('> clearToken');
      acapyToken.value = null;
      console.log('< clearToken');
    }

    return {
      loading,
      error,
      innkeeperReady,
      clearToken,
      login,
    };
  }
);

export default {
  useInnkeeperTokenStore,
};
