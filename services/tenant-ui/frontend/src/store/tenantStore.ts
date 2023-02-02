import { API_PATH } from '@/helpers/constants';
import { defineStore, storeToRefs } from 'pinia';
import { computed, ref, Ref } from 'vue';
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
  const publicDidRegistrationProgress: Ref<string> = ref('');
  const tenantConfig: any = ref(null);

  const { token } = storeToRefs(useTokenStore());
  const acapyApi = useAcapyApi();

  // getters
  const tenantReady = computed(() => {
    return token.value != null;
  });
  const isIssuer = computed(() => {
    return (
      endorserConnection.value &&
      endorserConnection.value.state === 'active' &&
      publicDid.value &&
      publicDid.value.result &&
      publicDid.value.result.did
    );
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

  async function getPublicDid() {
    console.log('> tenantStore.getPublicDid');
    error.value = null;
    loadingIssuance.value = true;

    await acapyApi
      .getHttp(API_PATH.WALLET_DID_PUBLIC)
      .then((res: any) => {
        publicDid.value = res.data;
      })
      .catch((err) => {
        error.value = err;
        publicDid.value = null;
      })
      .finally(() => {
        loadingIssuance.value = false;
      });
    console.log('< tenantStore.getPublicDid');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return publicDid.value;
  }

  async function registerPublicDid() {
    console.log('> contactsStore.registerPublicDid');
    error.value = null;
    loadingIssuance.value = true;
    publicDidRegistrationProgress.value = '';

    try {
      // Create a DID
      publicDidRegistrationProgress.value = 'Creating DID';
      const cRes = await acapyApi.postHttp(API_PATH.WALLET_DID_CREATE, {
        method: 'sov',
        options: { key_type: 'ed25519' },
      });
      console.log(cRes);
      if (!cRes.data.result) {
        throw Error('No result in create DID response');
      }

      // Use the did and verkey
      const did = cRes.data.result.did;
      const verkey = cRes.data.result.verkey;
      // Register the DID
      publicDidRegistrationProgress.value = 'Registering the DID';
      const rRes = await acapyApi.postHttp(
        `${API_PATH.TENANT_REGISTER_PUBLIC_DID}?did=${did}&verkey=${verkey}`,
        {}
      );
      console.log(rRes);

      // Give 2 seconds to wait
      // TODO: should this be here? Or register and assign as 2 different buttons...?
      await new Promise((r) => setTimeout(r, 2000));

      // Assign the public DID
      publicDidRegistrationProgress.value = 'Assigning the public DID';
      const aRes = await acapyApi.postHttp(
        `${API_PATH.WALLET_DID_PUBLIC}?did=${did}`,
        {}
      );
      console.log(aRes);

      // Give 2 seconds to wait then fetch it
      await new Promise((r) => setTimeout(r, 2000));
      publicDidRegistrationProgress.value = 'Fetching created public DID';
      getPublicDid();
    } catch (err) {
      error.value = err;
    } finally {
      loadingIssuance.value = false;
      publicDidRegistrationProgress.value = '';
    }
    console.log('< contactsStore.registerPublicDid');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
  }

  return {
    loading,
    loadingIssuance,
    error,
    tenant,
    endorserConnection,
    endorserInfo,
    publicDid,
    tenantReady,
    isIssuer,
    tenantConfig,
    publicDidRegistrationProgress,
    getSelf,
    clearTenant,
    getEndorserConnection,
    getEndorserInfo,
    connectToEndorser,
    getPublicDid,
    registerPublicDid,
  };
});

export default {
  useTenantStore,
};
