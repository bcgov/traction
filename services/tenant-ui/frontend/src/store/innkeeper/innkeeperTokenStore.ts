import axios from 'axios';
import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { useAcapyApi } from '../acapyApi';
import { Ref } from 'vue';
import { API_PATH } from '@/helpers/constants';

export const useInnkeeperTokenStore = defineStore(
  'useInnkeeperTokenStore',
  () => {
    const acapyApi = useAcapyApi();

    // state
    const token: Ref<string | null> = ref(null);
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
      await acapyApi
        .postHttp(API_PATH.MULTITENANCY_TENANT_TOKEN(params.adminName), payload)
        .then((res) => {
          token.value = res.data.token;
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
      console.log('< clearToken');
    }

    return {
      token,
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
