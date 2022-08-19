import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useTenantApi } from './tenantApi';

export const useTenantStore = defineStore('tenant', () => {
  // state
  const tenant: any = ref(null);
  const loading: any = ref(false);
  const error: any = ref(null);

  // getters

  // actions

  // grab the tenant api
  const tenantApi = useTenantApi();

  async function getSelf() {
    console.log('> tenantStore.getSelf');
    tenant.value = null;
    error.value = null;
    loading.value = true;

    tenantApi
      .getHttp('/tenant/v1/admin/self')
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
    console.log('< tenantStore.getSelf');

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

    tenantApi
      .postHttp('/tenant/v1/admin/make-issuer')
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

  return { tenant, loading, error, getSelf, makeIssuer };
});

export default {
  useTenantStore,
};
