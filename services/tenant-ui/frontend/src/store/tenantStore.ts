import { API_PATH } from '@/helpers/constants';
import { defineStore, storeToRefs } from 'pinia';
import { computed, ref } from 'vue';
import { useAcapyApi } from './acapyApi';
import { useTokenStore } from './tokenStore';

export const useTenantStore = defineStore('tenant', () => {
  // state
  const tenant: any = ref(null);
  const loading: any = ref(false);
  const loadingIssuance: any = ref(false);
  const error: any = ref(null);
  const endorserConnection: any = ref(null);
  const endorserInfo: any = ref(null);
  const publicDid: any = ref(null);
  const tenantConfig: any = ref(null);

  const { token } = storeToRefs(useTokenStore());
  const acapyApi = useAcapyApi();

  // getters
  const tenantReady = computed(() => {
    return token.value != null;
    // return token.value != null && tenant.value != null;
  });
  const isIssuer = computed(() => {
    return false;
    // return tenant.value.issuer;
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

    await acapyApi
      .getHttp(API_PATH.TENANT_SELF)
      .then((res: any) => {
        tenant.value = res.data;
      })
      .catch((err) => {
        error.value = err;
        tenant.value = null;
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

  async function getEndorserConnection() {
    console.log('> tenantStore.getEndorserConnection');
    error.value = null;
    loadingIssuance.value = true;

    await acapyApi
      .getHttp(API_PATH.TENANT_ENDORSER_CONNECTION)
      .then((res: any) => {
        endorserConnection.value = res.data;
      })
      .catch((err) => {
        error.value = err;
        endorserConnection.value = null;
      })
      .finally(() => {
        loadingIssuance.value = false;
      });
    console.log('< tenantStore.getEndorserConnection');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return endorserConnection.value;
  }

  async function getEndorserInfo() {
    console.log('> tenantStore.getEndorserInfo');
    error.value = null;
    loadingIssuance.value = true;

    await acapyApi
      .getHttp(API_PATH.TENANT_ENDORSER_INFO)
      .then((res: any) => {
        endorserInfo.value = res.data;
      })
      .catch((err) => {
        error.value = err;
        endorserInfo.value = null;
      })
      .finally(() => {
        loadingIssuance.value = false;
      });
    console.log('< tenantStore.getEndorserInfo');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return endorserInfo.value;
  }

  async function connectToEndorser() {
    console.log('> contactsStore.createInvitation');
    error.value = null;
    loadingIssuance.value = true;

    // need the await here since the returned invitationData is not one of our stored refs...
    await acapyApi
      .postHttp(API_PATH.TENANT_ENDORSER_CONNECTION, {})
      .then((res) => {
        console.log(res);
        endorserConnection.value = res.data;
      })
      .catch((err) => {
        error.value = err;
      })
      .finally(() => {
        loadingIssuance.value = false;
      });
    console.log('< contactsStore.connectToEndorser');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
  }

  // async function makeIssuer() {
  //   console.log('> tenantStore.makeIssuer');
  //   error.value = null;
  //   loading.value = true;

  //   tenantApi
  //     .postHttp(API_PATH.TENANT_MAKE_ISSUER)
  //     .then((res) => {
  //       console.log(res);
  //       tenant.value = res.data.item;
  //       console.log(tenant.value);
  //     })
  //     .catch((err) => {
  //       error.value = err;
  //       console.log(error.value);
  //     })
  //     .finally(() => {
  //       loading.value = false;
  //     });
  //   console.log('< tenantStore.makeIssuer');

  //   if (error.value != null) {
  //     // throw error so $onAction.onError listeners can add their own handler
  //     throw error.value;
  //   }
  //   // return data so $onAction.after listeners can add their own handler
  //   return tenant.value;
  // }

  // async function getConfiguration() {
  //   console.log('> tenantStore.getConfiguration');
  //   error.value = null;
  //   loading.value = true;

  //   await tenantApi
  //     .getHttp(API_PATH.TENANT_CONFIGURATION)
  //     .then((res) => {
  //       console.log(res);
  //       tenantConfig.value = res.data.item;
  //       console.log(tenant.value);
  //     })
  //     .catch((err) => {
  //       error.value = err;
  //       tenantConfig.value = null;
  //     })
  //     .finally(() => {
  //       loading.value = false;
  //     });
  //   console.log('< tenantStore.getConfiguration');

  //   if (error.value != null) {
  //     // throw error so $onAction.onError listeners can add their own handler
  //     throw error.value;
  //   }
  //   // return data so $onAction.after listeners can add their own handler
  //   return tenantConfig.value;
  // }

  // async function updateConfiguration(payload: any = {}) {
  //   console.log('> tenantStore.updateConfiguration');
  //   error.value = null;
  //   loading.value = true;
  //   console.log(payload);
  //   await tenantApi
  //     .putHttp(API_PATH.TENANT_CONFIGURATION, payload)
  //     .then((res) => {
  //       console.log(res);
  //       tenantConfig.value = res.data.item;
  //       console.log(tenant.value);
  //     })
  //     .catch((err) => {
  //       error.value = err;
  //       console.log(error.value);
  //     })
  //     .finally(() => {
  //       loading.value = false;
  //     });
  //   console.log('< tenantStore.updateConfiguration');

  //   if (error.value != null) {
  //     // throw error so $onAction.onError listeners can add their own handler
  //     throw error.value;
  //   }
  //   // return data so $onAction.after listeners can add their own handler
  //   return tenantConfig.value;
  // }

  return {
    tenant,
    endorserConnection,
    endorserInfo,
    loading,
    loadingIssuance,
    error,
    tenantReady,
    getSelf,
    // makeIssuer,
    clearTenant,
    getEndorserConnection,
    getEndorserInfo,
    connectToEndorser,
    isIssuer,
    // getConfiguration,
    // updateConfiguration,
    tenantConfig,
  };
});

export default {
  useTenantStore,
};
