import { EndorserInfo, TAAInfo } from '@/types/acapyApi/acapyInterface';

import { API_PATH } from '@/helpers/constants';
import { defineStore, storeToRefs } from 'pinia';
import { computed, ref, Ref } from 'vue';
import { useAcapyApi } from './acapyApi';
import { useTokenStore } from './tokenStore';
import { fetchItem } from './utils/fetchItem';

export const useTenantStore = defineStore('tenant', () => {
  // state
  const tenant: any = ref(null);
  const loading: Ref<boolean> = ref(false);
  const loadingIssuance: Ref<boolean> = ref(false);
  const error: any = ref(null);
  const endorserConnection: any = ref(null);
  const endorserInfo: Ref<EndorserInfo | null> = ref(null);
  const publicDid: any = ref(null);
  const writeLedger: any = ref(null);
  const publicDidRegistrationProgress: Ref<string> = ref('');
  const taa: Ref<any> = ref(null);
  const tenantConfig: any = ref(null);
  const tenantWallet: any = ref(null);
  const tenantDefaultSettings: any = ref(null);

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
      publicDid.value.did
    );
  });

  // actions
  function clearTenant() {
    console.log('> clearTenant');
    tenant.value = null;
    localStorage.removeItem('tenant');
    localStorage.removeItem('tenantConfig');
    localStorage.removeItem('tenantTaa');
    localStorage.removeItem('tenantEndorserInfo');
    localStorage.removeItem('tenantEndorserConnection');
    console.log('< clearTenant');
  }

  async function getSelf() {
    tenant.value = await fetchItem(API_PATH.TENANT_SELF, '', error, loading);
    localStorage.setItem('tenant', JSON.stringify(tenant.value));
  }

  async function getTenantConfig() {
    tenantConfig.value = await fetchItem(
      API_PATH.TENANT_CONFIG,
      '',
      error,
      loading
    );
    localStorage.setItem('tenantConfig', JSON.stringify(tenantConfig.value));
    if (tenantConfig.value.curr_ledger_id) {
      writeLedger.value = {
        ledger_id: tenantConfig.value.curr_ledger_id,
      };
    }
  }

  async function getIssuanceStatus() {
    console.log('> tenantStore.getIssuanceStatus');
    loadingIssuance.value = true;
    // Find out issuer status when logging in
    const result = await Promise.allSettled([
      getTaa(),
      getEndorserInfo(),
      getEndorserConnection(),
      getPublicDid(),
    ]);
    loadingIssuance.value = false;
    if (result) {
      const errors = result.filter(
        (res): res is PromiseRejectedResult => res.status === 'rejected'
      );
      if (errors?.length) {
        console.log(errors);
        throw Error(errors[0]?.reason);
      }
    }
    console.log('< tenantStore.getIssuanceStatus');
  }

  async function getEndorserConnection() {
    console.log('> tenantStore.getEndorserConnection');
    // Don't override the loader if it's already going from something else
    const loadingTrack = !loadingIssuance.value ? loadingIssuance : ref(false);
    error.value = null;
    loadingTrack.value = true;

    await acapyApi
      .getHttp(API_PATH.TENANT_ENDORSER_CONNECTION)
      .then((res: any) => {
        endorserConnection.value = res.data;
        localStorage.setItem(
          'tenantEndorserConnection',
          JSON.stringify(endorserConnection.value)
        );
      })
      .catch((err) => {
        endorserConnection.value = null;
        if (err.response && err.response.status === 404) {
          // 404s are not errors here
        } else {
          error.value = err;
        }
      })
      .finally(() => {
        loadingTrack.value = false;
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
    // Don't override the loader if it's already going from something else
    const loadingTrack = !loadingIssuance.value ? loadingIssuance : ref(false);
    error.value = null;
    loadingTrack.value = true;

    await acapyApi
      .getHttp(API_PATH.TENANT_ENDORSER_INFO)
      .then((res: any) => {
        endorserInfo.value = res.data;
        localStorage.setItem(
          'tenantEndorderInfo',
          JSON.stringify(endorserInfo.value)
        );
      })
      .catch((err) => {
        error.value = err;
        endorserInfo.value = null;
      })
      .finally(() => {
        loadingTrack.value = false;
      });
    console.log('< tenantStore.getEndorserInfo');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return endorserInfo.value;
  }

  async function getEndorserConnectionState(connId: string) {
    console.log('> tenantStore.getEndorserConnectionState');
    error.value = null;
    loadingIssuance.value = true;
    let status: any = null;
    await acapyApi
      .getHttp(API_PATH.CONNECTION(connId), {})
      .then((res) => {
        status = res.data.state;
      })
      .catch((err) => {
        error.value = err;
      })
      .finally(() => {
        loadingIssuance.value = false;
        getEndorserInfo();
      });
    console.log('< tenantStore.getEndorserConnectionState');
    return status;
  }

  async function connectToEndorser() {
    console.log('> tenantStore.connectToEndorser');
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
    console.log('< tenantStore.connectToEndorser');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
  }

  async function getPublicDid() {
    publicDid.value = await fetchItem(
      API_PATH.WALLET_DID_PUBLIC,
      '',
      error,
      !loadingIssuance.value ? loadingIssuance : ref(false)
    );
    localStorage.setItem('tenantPublicDid', JSON.stringify(publicDid.value));
  }

  async function getWriteLedger() {
    console.log('> tenantStore.getWriteLedger');
    writeLedger.value = await fetchItem(
      API_PATH.TENANT_GET_WRITE_LEDGER,
      '',
      error,
      !loadingIssuance.value ? loadingIssuance : ref(false)
    );
  }

  async function setWriteLedger(ledger_id: string) {
    console.log('> tenantStore.setWriteLedger');
    const res = await acapyApi.putHttp(
      API_PATH.TENANT_SWITCH_WRITE_LEDGER(ledger_id)
    );
    if (!res.data.write_ledger) {
      throw Error('No write_ledger in set write ledger response');
    }
    const curr_ledger_id = res.data.write_ledger;
    writeLedger.value = {
      ledger_id: curr_ledger_id,
    };
    console.log('< tenantStore.setWriteLedger');
  }

  async function waitForTxnCompletion(txnId: string) {
    let retries = 0;
    for (;;) {
      const pRes = await acapyApi.getHttp(API_PATH.TRANSACTION_GET(txnId));
      if (pRes.data.state === 'transaction_acked') {
        return;
      }
      retries = retries + 1;
      const wait_interval = Math.pow(3, 1 + 0.25 * (retries - 1));
      await new Promise((r) => setTimeout(r, wait_interval));
    }
  }

  async function registerPublicDid() {
    console.log('> connectionStore.registerPublicDid');
    error.value = null;
    loadingIssuance.value = true;
    publicDidRegistrationProgress.value = '';
    let postedDID: any = null;
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
      const alias = tenant.value.tenant_name || tenant.value.wallet_id;
      // Register the DID
      publicDidRegistrationProgress.value = 'Registering the DID';
      const rRes = await acapyApi.postHttp(
        `${API_PATH.TENANT_REGISTER_PUBLIC_DID}?did=${did}&verkey=${verkey}&alias=${alias}`,
        {}
      );
      console.log(rRes);
      console.log(`posted ${did} on ledger ${writeLedger.value.ledger_id}`);

      // TODO: should this be here? Or register and assign as 2 different buttons...?
      // Wait for endorse transaction completion
      const txnId = rRes.data.txn.transaction_id;
      await waitForTxnCompletion(txnId);
      // Verify DID is posted on correct ledger
      const pRes = await acapyApi.getHttp(
        `${API_PATH.TENANT_GET_VERKEY_POSTED_DID}?did=${did}`,
        {}
      );
      if (!pRes.data.verkey) {
        console.log(`DID ${did} is not posted on ledger`);
        postedDID = null;
      } else if (pRes.data && pRes.data.ledger_id) {
        const posted_did_ledger_id = pRes.data.ledger_id;
        console.log(
          `Verified DID ${did} is posted on ledger ${posted_did_ledger_id}`
        );
        if (posted_did_ledger_id === writeLedger.value.ledger_id) {
          postedDID = did;
        } else {
          postedDID = null;
        }
      } else {
        postedDID = did;
      }
    } catch (err) {
      error.value = err;
    } finally {
      loadingIssuance.value = false;
      publicDidRegistrationProgress.value = '';
    }
    console.log('< connectionStore.registerPublicDid');
    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    return postedDID;
  }

  async function assignPublicDid(did: string) {
    console.log('> connectionStore.assignPublicDid');
    error.value = null;
    loadingIssuance.value = true;
    publicDidRegistrationProgress.value = '';
    try {
      // Assign the public DID
      publicDidRegistrationProgress.value = 'Assigning the public DID';
      const aRes = await acapyApi.postHttp(
        `${API_PATH.WALLET_DID_PUBLIC}?did=${did}`,
        {}
      );
      console.log(aRes);

      publicDidRegistrationProgress.value = 'Fetching created public DID';
      getPublicDid();
    } catch (err) {
      error.value = err;
    } finally {
      loadingIssuance.value = false;
      publicDidRegistrationProgress.value = '';
      // set curr_ledger_id in TenantRecord
      const payload = {
        ledger_id: writeLedger.value.ledger_id,
      };
      const cRes = await acapyApi.putHttp(
        API_PATH.TENANT_CONFIG_SET_LEDGER_ID,
        payload
      );
      getWriteLedger();
    }
    console.log('< connectionStore.assignPublicDid');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
  }

  async function getTenantSubWallet() {
    console.log('> tenantStore.getSubWallet');
    error.value = null;
    loading.value = true;

    await acapyApi
      .getHttp(API_PATH.TENANT_WALLET)
      .then((res: any) => {
        tenantWallet.value = res.data;
      })
      .catch((err) => {
        error.value = err;
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< tenantStore.getSubWallet');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return tenantWallet.value;
  }

  async function getTenantDefaultSettings() {
    console.log('> tenantStore.getTenantDefaultSettings');
    error.value = null;
    loading.value = true;
    tenantDefaultSettings.value = await fetchItem(
      API_PATH.TENANT_SETTINGS,
      '',
      error,
      loading
    );
    console.log('< tenantStore.getTenantDefaultSettings');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
    // return data so $onAction.after listeners can add their own handler
    return tenantDefaultSettings.value;
  }

  async function updateTenantSubWallet(payload: object) {
    console.log('> tenantStore.updateTenantSubWallet');
    error.value = null;
    loading.value = true;

    await acapyApi
      .putHttp(API_PATH.TENANT_WALLET, payload)
      .then((res) => {
        console.log(res);
      })
      .catch((err) => {
        error.value = err;
      })
      .finally(() => {
        loading.value = false;
      });
    console.log('< tenantStore.updateTenantSubWallet');

    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
  }

  async function getTaa() {
    taa.value = await fetchItem(
      API_PATH.LEDGER_TAA,
      '',
      error,
      !loadingIssuance.value ? loadingIssuance : ref(false)
    );
    localStorage.setItem('tenantTaa', JSON.stringify(taa.value));
  }

  async function acceptTaa(payload: object) {
    console.log('> tenantStore.acceptTaa');
    error.value = null;
    loadingIssuance.value = true;

    try {
      await acapyApi.postHttp(API_PATH.LEDGER_TAA_ACCEPT, payload);
      await getTaa();
    } catch (err) {
      error.value = err;
    } finally {
      loadingIssuance.value = false;
    }
    console.log('< tenantStore.acceptTaa');
    if (error.value != null) {
      // throw error so $onAction.onError listeners can add their own handler
      throw error.value;
    }
  }

  function setTenantLoginDataFromLocalStorage() {
    console.log('> setTenantFromLocalStorage');
    try {
      const savedTenant = localStorage.getItem('tenant');
      tenant.value = savedTenant ? JSON.parse(savedTenant) : null;

      const savedTenantConfig = localStorage.getItem('tenantConfig');
      tenantConfig.value = savedTenantConfig
        ? JSON.parse(savedTenantConfig)
        : null;

      const savedTaa = localStorage.getItem('tenantTaa');
      taa.value = savedTaa ? JSON.parse(savedTaa) : null;

      const savedEndorserInfo = localStorage.getItem('tenantEndorserInfo');
      endorserInfo.value = savedEndorserInfo
        ? JSON.parse(savedEndorserInfo)
        : null;

      const savedEndorserConnection = localStorage.getItem(
        'tenantEndorserConnection'
      );
      endorserConnection.value = savedEndorserConnection
        ? JSON.parse(savedEndorserConnection)
        : null;

      const savedPublicDid = localStorage.getItem('tenantPublicDid');
      publicDid.value = savedPublicDid ? JSON.parse(savedPublicDid) : null;
    } catch (err) {
      console.info('Error processing tenant info from local storage');
      console.error(err);
    }

    console.log('< setTenantFromLocalStorage');
  }

  return {
    loading,
    loadingIssuance,
    error,
    tenant,
    endorserConnection,
    endorserInfo,
    publicDid,
    writeLedger,
    taa,
    tenantReady,
    isIssuer,
    publicDidRegistrationProgress,
    tenantConfig,
    tenantWallet,
    tenantDefaultSettings,
    getSelf,
    getTenantConfig,
    getIssuanceStatus,
    clearTenant,
    setTenantLoginDataFromLocalStorage,
    getEndorserConnection,
    getEndorserInfo,
    getTenantDefaultSettings,
    getEndorserConnectionState,
    connectToEndorser,
    getPublicDid,
    getWriteLedger,
    setWriteLedger,
    registerPublicDid,
    assignPublicDid,
    getTenantSubWallet,
    updateTenantSubWallet,
    getTaa,
    acceptTaa,
  };
});

export default {
  useTenantStore,
};
