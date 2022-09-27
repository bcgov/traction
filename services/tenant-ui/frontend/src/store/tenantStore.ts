import { defineStore, storeToRefs } from 'pinia';
import { computed, ref } from 'vue';
import { useTenantApi } from './tenantApi';
import { useTokenStore } from './tokenStore';

export const useTenantStore = defineStore('tenant', () => {
  // state
  const tenant: any = ref(null);
  const loading: any = ref(false);
  const error: any = ref(null);
  const tenantConfig: any = ref(null);

  const { token } = storeToRefs(useTokenStore());
  const tenantApi = useTenantApi();

  // getters
  const tenantReady = computed(() => {
    return token.value != null && tenant.value != null;
  });

  const isIssuer = computed(() => {
    return tenant.value.issuer;
  });

  // actions
  function clearTenant() {
    console.log('> clearTenant');
    tenant.value = null;
    console.log('< clearTenant');
  }

  async function getSelf() {
    console.log('> tenantStore.getSelf');
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
        tenant.value = null;
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
        console.log(error.value);
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

  async function getConfiguration() {
    console.log('> tenantStore.getConfiguration');
    error.value = null;
    loading.value = true;

    await tenantApi
      .getHttp('/tenant/v1/admin/configuration')
      .then((res) => {
        console.log(res);
        tenantConfig.value = res.data.item;
        console.log(tenant.value);
      })
      .catch((err) => {
        error.value = err;
        tenantConfig.value = null;
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< tenantStore.getConfiguration');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return tenantConfig.value;
  }

  async function updateConfiguration(payload: any = {}) {
    console.log('> tenantStore.updateConfiguration');
    error.value = null;
    loading.value = true;
    console.log(payload);
    await tenantApi
      .putHttp('/tenant/v1/admin/configuration', payload)
      .then((res) => {
        console.log(res);
        tenantConfig.value = res.data.item;
        console.log(tenant.value);
      })
      .catch((err) => {
        error.value = err;
        console.log(error.value);
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< tenantStore.updateConfiguration');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return tenantConfig.value;
  }

  return {
    tenant,
    loading,
    error,
    tenantReady,
    getSelf,
    makeIssuer,
    clearTenant,
    isIssuer,
    getConfiguration,
    updateConfiguration,
    tenantConfig,
  };
});

export default {
  useTenantStore,
};
