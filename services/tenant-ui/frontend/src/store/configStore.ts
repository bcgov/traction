import { AdminModules } from '@/types/acapyApi/acapyInterface';

import { Ref, ref } from 'vue';
import { defineStore } from 'pinia';
import axios from 'axios';
import { API_PATH } from '@/helpers/constants';
import { fetchList } from './utils';

export const useConfigStore = defineStore('config', () => {
  // state
  const acapyPlugins: Ref<AdminModules[]> = ref([]);
  const config: any = ref(null);
  const loading: any = ref(false);
  const error: any = ref(null);

  // getters
  function proxyPath(p: string) {
    if (config.value) {
      let pp = config.value.frontend.tenantProxyPath;
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

  async function getPluginList() {
    return fetchList(API_PATH.SERVER_PLUGINS, acapyPlugins, error, loading);
  }

  return {
    acapyPlugins,
    config,
    loading,
    error,
    load,
    proxyPath,
    getPluginList,
  };
});

export default {
  useConfigStore,
};
