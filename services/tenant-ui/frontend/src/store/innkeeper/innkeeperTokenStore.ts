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
    const { token } = storeToRefs(useTokenStore());
    // A raw api call without using the interceptors from the acapyApiTenantStore
    const api = axios.create({
      baseURL: config.value.frontend.tenantProxyPath,
    });

    // state
    const loading: Ref<boolean> = ref(false);
    const error: Ref<string | null> = ref(null);

    // getters
    const innkeeperReady = computed((): boolean => {
      return token.value != null;
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
      token.value = null;
      error.value = null;
      loading.value = true;

      // TODO: isolate this to something reusable when we grab an axios connection.
      await api
        .post(API_PATH.MULTITENANCY_TENANT_TOKEN(params.adminName), payload)
        .then((res) => {
          token.value = res.data.token;
          if (token.value) localStorage.setItem('innkeeper-token', token.value);
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
      return token.value;
    }

    function clearToken(): void {
      console.log('> clearToken');
      token.value = null;
      localStorage.removeItem('innkeeper-token');
      console.log('< clearToken');
    }

    function setToken(newToken: string) {
      console.log('> setToken');
      token.value = newToken;
      console.log('< setToken');
    }

    return {
      loading,
      error,
      innkeeperReady,
      clearToken,
      setToken,
      login,
    };
  }
);

export default {
  useInnkeeperTokenStore,
};
