import { defineStore } from 'pinia';
import { ref } from 'vue';
import axios from 'axios';
import { useConfigStore } from './configStore';
import { useTokenStore } from './tokenStore';

export const useTenantStore = defineStore('tenant', () => {
  // state
  const tenant: any = ref(null);
  const loading: any = ref(false);
  const error: any = ref(null);

  // getters

  // actions
  async function load() {
    console.log('> tenantStore.load');
    tenant.value = null;
    error.value = null;
    loading.value = true;

    // TODO: isolate this to something reusable when we grab an axios connection.
    const configStore = useConfigStore();
    const url = configStore.proxyPath('/tenant/v1/admin/self');
    const tokenStore = useTokenStore();
    if (!tokenStore.token) {
      return;
    }

    await axios({
      method: 'get',
      url: url,
      headers: {
        accept: 'application/json',
        Authorization: `Bearer ${tokenStore.token}`,
      },
    })
      .then((res) => {
        console.log(res);
        tenant.value = res.data.item;
        console.log(tenant.value);
      })
      .catch((err) => {
        error.value = err;
        //console.log(error.value);
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< tenantStore.load');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return tenant.value;
  }

  async function makeIssuer() {
    console.log('> tenantStore.makeIssuer');
    error.value = null;
    loading.value = true;

    // TODO: isolate this to something reusable when we grab an axios connection.
    const configStore = useConfigStore();
    const url = configStore.proxyPath('/tenant/v1/admin/make-issuer');
    const tokenStore = useTokenStore();
    if (!tokenStore.token) {
      return;
    }
    await axios({
      method: 'post',
      url: url,
      headers: {
        accept: 'application/json',
        Authorization: `Bearer ${tokenStore.token}`,
      },
      data: {},
    })
      .then((res) => {
        console.log(res);
        tenant.value = res.data.item;
        console.log(tenant.value);
      })
      .catch((err) => {
        error.value = err;
        //console.log(error.value);
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< tenantStore.makeIssuer');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return tenant.value;
  }

  return { tenant, loading, error, load, makeIssuer };
});

export default {
  useTenantStore,
};
