import { defineStore } from 'pinia';
import { ref } from 'vue';
import axios from 'axios';
import { API_PATH } from '@/helpers/constants';

export const useConfigStore = defineStore('config', () => {
  // state
  const config: any = ref(null);
  const loading: any = ref(false);
  const error: any = ref(null);

  // getters
  function proxyPath(p: string) {
    if (config.value) {
      let pp = config.value.frontend.proxyPath;
      if (pp.endsWith('/')) {
        pp = pp.slice(0, -1);
      }
      if (!p.startsWith('/')) {
        p = `/${p}`;
      }

      return `${pp}${p}`;
    } else {
      // ?? error ??
      return p;
    }
  }

  // actions
  async function load() {
    console.log('> configStore.load');
    config.value = null;
    error.value = null;
    loading.value = true;
    await axios
      .get(API_PATH.CONFIG)
      .then((res) => {
        console.log(res);
        config.value = res.data;
      })
      .catch((err) => {
        error.value = err;
        // console.log(error.value);
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< configStore.load');
    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return config.value;
  }

  return { config, loading, error, load, proxyPath };
});

export default {
  useConfigStore,
};
