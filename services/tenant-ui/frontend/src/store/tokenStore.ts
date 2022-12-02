import { defineStore } from 'pinia';
import { ref } from 'vue';
import axios from 'axios';
import { useConfigStore } from './configStore';
import jwtDecode from 'jwt-decode';
import { API_PATH } from '@/helpers/constants';

export const useTokenStore = defineStore('token', () => {
  // state
  const token: any = ref(null);
  const acapyToken: any = ref(null);
  const loading: any = ref(false);
  const error: any = ref(null);

  // getters

  // actions
  async function login(username: string, password: string) {
    console.log('> tokenStore.load');
    const payload = `username=${username}&password=${password}`;
    token.value = null;
    acapyToken.value = null;
    error.value = null;
    loading.value = true;

    // TODO: isolate this to something reusable when we grab an axios connection.
    const configStore = useConfigStore();
    const url = configStore.proxyPath(API_PATH.TENANT_TOKEN);
    await axios({
      method: 'post',
      url,
      headers: {
        accept: 'application/json',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
      },
      data: payload,
    })
      .then((res) => {
        console.log(res);
        token.value = res.data.access_token;
        // parse out the acapy token and store that...
        try {
          const decoded = jwtDecode<any>(res.data.access_token);
          acapyToken.value = decoded.key;
        } catch (error) {
          console.error(`Error decoding acapy token : {}`, error);
        }
      })
      .catch((err) => {
        error.value = err;
        console.log(error.value);
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< tokenStore.load');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return token.value;
  }

  function clearToken() {
    console.log('> clearToken');
    token.value = null;
    acapyToken.value = null;
    console.log('< clearToken');
  }

  return { acapyToken, token, loading, error, clearToken, login };
});

export default {
  useTokenStore,
};
